from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from .affinity import AffinityEngine
from .cache_manager import CacheManager
from .config import (
    ADS_EVERY_N_CONTENT,
    BREAK_BUDGET_SEC,
    CACHE_LIMIT_BYTES,
    CHANNEL_NAME,
    CONTENT_AD_BIAS,
    MAX_READY_AHEAD,
    PLAYBACK_MODE,
    STATE_PATH,
    ensure_dirs,
)
from .models import EngineSnapshot, ItemKind, ItemStatus, ProgramItem
from .youtube_source import find_ad, find_content

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChannelEngine:
    def __init__(self) -> None:
        ensure_dirs()
        self.affinity = AffinityEngine()
        self.cache = CacheManager()
        self.queue: list[ProgramItem] = []
        self.current: Optional[ProgramItem] = None
        self.as_run: list[dict[str, Any]] = []
        self.logs: list[str] = []
        self.content_since_break = 0
        self.status = "starting"
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._load_state()

    def log(self, message: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        self.logs.append(line)
        self.logs = self.logs[-80:]
        logger.info(message)

    def _load_state(self) -> None:
        if not STATE_PATH.exists():
            return
        try:
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            self.affinity.load(data.get("affinity") or {})
            self.content_since_break = int(data.get("content_since_break") or 0)
            self.log("estado de afinidade restaurado")
        except Exception as exc:
            self.log(f"falha ao carregar estado: {exc}")

    def _save_state(self) -> None:
        payload = {
            "affinity": self.affinity.dump(),
            "content_since_break": self.content_since_break,
            "saved_at": _now(),
        }
        STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="channel-engine", daemon=True)
        self._thread.start()
        self.log("engine iniciada")

    def stop(self) -> None:
        self._stop.set()
        self.status = "stopped"

    def snapshot(self) -> EngineSnapshot:
        with self._lock:
            used = self.cache.used_bytes([*([self.current] if self.current else []), *self.queue])
            return EngineSnapshot(
                channel_name=CHANNEL_NAME,
                playback_mode=PLAYBACK_MODE,
                current=self.current,
                queue=list(self.queue),
                affinity=dict(self.affinity.weights),
                view_stats=self.affinity.view_stats,
                cache_used_bytes=used,
                cache_limit_bytes=CACHE_LIMIT_BYTES,
                cache_pct=round(100.0 * used / max(CACHE_LIMIT_BYTES, 1), 2),
                recent_as_run=list(self.as_run[-12:]),
                algorithm_log=list(self.logs[-40:]),
                content_since_break=self.content_since_break,
                status=self.status,
            )

    def _active_ids(self) -> set[str]:
        ids = set()
        if self.current and self.current.video_id:
            ids.add(self.current.video_id)
        for item in self.queue:
            if item.video_id:
                ids.add(item.video_id)
        for row in self.as_run[-30:]:
            if row.get("video_id"):
                ids.add(row["video_id"])
        return ids

    def _make_content(self) -> ProgramItem:
        ctype, reason = self.affinity.pick_content_type()
        self.log(f"selecionando conteúdo: {reason}")
        found = find_content(ctype, exclude_ids=self._active_ids())
        assert found
        item = ProgramItem(
            id=str(uuid.uuid4())[:8],
            kind=ItemKind.content,
            video_id=found["video_id"],
            title=found.get("title") or "conteúdo",
            duration_sec=float(found.get("duration") or 180),
            size_bytes=int(found.get("size_bytes") or 0),
            status=ItemStatus.planned,
            content_type=found.get("content_type") or ctype,
            matched_query=found.get("matched_query"),
            is_fallback=bool(found.get("is_fallback")),
        )
        return item

    def _pick_ad_type(self, content_type: Optional[str]) -> str:
        biased = CONTENT_AD_BIAS.get(content_type or "", [])
        pool = biased + ["spot_30", "generic_brand", "promo_house"]
        # prioriza tipos ligados ao conteúdo quente
        return pool[0]

    def _make_break(self, after_content_type: Optional[str]) -> list[ProgramItem]:
        budget = float(BREAK_BUDGET_SEC)
        ads: list[ProgramItem] = []
        while budget >= 12 and len(ads) < 2:
            ad_type = self._pick_ad_type(after_content_type)
            if ads:
                ad_type = "promo_house" if ad_type != "promo_house" else "generic_brand"
            self.log(f"planejando ad tipo={ad_type} budget={budget:.0f}s")
            found = find_ad(ad_type, exclude_ids=self._active_ids() | {a.video_id for a in ads})
            if not found:
                break
            dur = float(found.get("duration") or found.get("target_duration_sec") or 15)
            if dur > budget + 5:
                break
            item = ProgramItem(
                id=str(uuid.uuid4())[:8],
                kind=ItemKind.ad,
                video_id=found["video_id"],
                title=found.get("title") or f"Propaganda {ad_type}",
                duration_sec=dur,
                size_bytes=int(found.get("size_bytes") or 0),
                status=ItemStatus.planned,
                ad_type=found.get("ad_type") or ad_type,
                target_duration_sec=float(found.get("target_duration_sec") or dur),
                matched_query=found.get("matched_query"),
                match_score=found.get("match_score"),
                is_fallback=bool(found.get("is_fallback")),
            )
            ads.append(item)
            budget -= dur
        return ads

    def _prepare(self, item: ProgramItem) -> bool:
        tracked = [*([self.current] if self.current else []), *self.queue]
        if not self.cache.can_fit(tracked, item.size_bytes):
            # tenta encolher estimativa lógica se estiver apertado
            item.size_bytes = min(item.size_bytes, max(self.cache.free_bytes(tracked), 1))
            if not self.cache.can_fit(tracked, item.size_bytes):
                self.log(f"sem espaço no cache 2GB para {item.id}")
                return False
        item.status = ItemStatus.downloading
        # modo embed: não baixa mídia; marca stub ready (poupa armazenamento local)
        self.cache.mark_ready_stub(item)
        item.status = ItemStatus.ready
        self.log(f"ready {item.kind.value}:{item.title[:40]} ({item.video_id})")
        return True

    def _ensure_queue(self) -> None:
        ready_or_planned = [i for i in self.queue if i.status in {ItemStatus.ready, ItemStatus.planned, ItemStatus.downloading}]
        while len(ready_or_planned) < MAX_READY_AHEAD + 1:
            if self.content_since_break >= ADS_EVERY_N_CONTENT:
                prev_type = self.current.content_type if self.current else None
                ads = self._make_break(prev_type)
                for ad in ads:
                    self.queue.append(ad)
                self.content_since_break = 0
                self.log(f"break comercial inserido ({len(ads)} spots)")
            else:
                content = self._make_content()
                self.queue.append(content)
                self.content_since_break += 1
            ready_or_planned = [i for i in self.queue if i.status in {ItemStatus.ready, ItemStatus.planned, ItemStatus.downloading}]

        # prefetch do próximo
        for item in self.queue:
            if item.status == ItemStatus.planned:
                ok = self._prepare(item)
                if not ok:
                    item.status = ItemStatus.failed
                break

    def _promote_next(self) -> None:
        while self.queue and self.queue[0].status == ItemStatus.failed:
            bad = self.queue.pop(0)
            self.log(f"removendo failed {bad.id}")

        if not self.queue:
            self._ensure_queue()

        nxt = self.queue.pop(0)
        if nxt.status != ItemStatus.ready:
            self._prepare(nxt)
        nxt.status = ItemStatus.playing
        nxt.watched_sec = 0
        nxt.watched_ratio = 0
        nxt.completed = False
        self.current = nxt
        self.status = "on_air"
        self.log(f"NO AR → {nxt.kind.value}: {nxt.title[:50]}")

    def report_progress(self, watched_sec: float, duration_sec: float | None = None) -> dict[str, Any]:
        with self._lock:
            if not self.current:
                return {"ok": False}
            dur = duration_sec or self.current.duration_sec or 1
            self.current.duration_sec = dur
            self.current.watched_sec = max(0.0, watched_sec)
            self.current.watched_ratio = min(1.0, watched_sec / max(dur, 1))
            return {"ok": True, "ratio": self.current.watched_ratio}

    def report_ended(self) -> dict[str, Any]:
        with self._lock:
            return self._finish_current(completed=True)

    def _finish_current(self, completed: bool) -> dict[str, Any]:
        cur = self.current
        if not cur:
            self._promote_next()
            return {"ok": True, "next": self.current.public_dict() if self.current else None}

        if completed:
            cur.watched_ratio = max(cur.watched_ratio, 1.0)
            cur.watched_sec = max(cur.watched_sec, cur.duration_sec)
            cur.completed = True

        if cur.kind == ItemKind.content and cur.content_type:
            msg = self.affinity.record_view(cur.content_type, cur.watched_ratio, cur.watched_sec)
            self.log(msg)

        self.as_run.append(
            {
                "at": _now(),
                "video_id": cur.video_id,
                "kind": cur.kind.value,
                "title": cur.title,
                "content_type": cur.content_type,
                "ad_type": cur.ad_type,
                "watched_ratio": round(cur.watched_ratio, 3),
                "completed": cur.completed,
                "duration_sec": cur.duration_sec,
            }
        )
        self.as_run = self.as_run[-100:]

        self.cache.evict(cur)
        cur.status = ItemStatus.deleted
        self.log(f"evicto do cache: {cur.id}")
        self.current = None
        self._ensure_queue()
        self._promote_next()
        self._save_state()
        return {"ok": True, "next": self.current.public_dict() if self.current else None}

    def _loop(self) -> None:
        try:
            with self._lock:
                self._ensure_queue()
                if not self.current:
                    self._promote_next()
            self.status = "on_air"
            while not self._stop.is_set():
                with self._lock:
                    self._ensure_queue()
                    # watchdog: se item atual expirou sem evento do player
                    if self.current and self.current.duration_sec > 0:
                        # sem heartbeat do front, não força fim agressivo
                        pass
                time.sleep(2)
        except Exception as exc:
            self.status = "error"
            self.log(f"engine error: {exc}")
            logger.exception("engine crash")


engine = ChannelEngine()
