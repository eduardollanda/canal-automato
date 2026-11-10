from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class VideoHistory:
    """Histórico persistente de vídeos já exibidos (anti-repetição)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.RLock()
        self._by_id: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        with self._lock:
            if not self.path.exists():
                self._by_id = {}
                return
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                items = data.get("items") if isinstance(data, dict) else data
                by_id: dict[str, dict[str, Any]] = {}
                for row in items or []:
                    vid = str(row.get("video_id") or "").strip()
                    if not vid:
                        continue
                    by_id[vid] = {
                        "video_id": vid,
                        "title": row.get("title") or "",
                        "kind": row.get("kind") or "content",
                        "content_type": row.get("content_type"),
                        "ad_type": row.get("ad_type"),
                        "played_at": row.get("played_at") or _now(),
                    }
                self._by_id = by_id
                logger.info("histórico carregado: %s vídeos em %s", len(self._by_id), self.path)
            except Exception as exc:
                logger.warning("falha ao carregar histórico: %s", exc)
                self._by_id = {}

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "saved_at": _now(),
                "count": len(self._by_id),
                "items": list(self._by_id.values()),
            }
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.path)

    def seen_ids(self) -> set[str]:
        with self._lock:
            return set(self._by_id.keys())

    def count(self) -> int:
        with self._lock:
            return len(self._by_id)

    def contains(self, video_id: str) -> bool:
        with self._lock:
            return video_id in self._by_id

    def record(
        self,
        *,
        video_id: str,
        title: str = "",
        kind: str = "content",
        content_type: Optional[str] = None,
        ad_type: Optional[str] = None,
        played_at: Optional[str] = None,
    ) -> bool:
        """Registra vídeo. Retorna True se for a primeira ocorrência."""
        video_id = (video_id or "").strip()
        if not video_id:
            return False
        with self._lock:
            is_new = video_id not in self._by_id
            prev = self._by_id.get(video_id) or {}
            self._by_id[video_id] = {
                "video_id": video_id,
                "title": title or prev.get("title") or "",
                "kind": kind or prev.get("kind") or "content",
                "content_type": content_type if content_type is not None else prev.get("content_type"),
                "ad_type": ad_type if ad_type is not None else prev.get("ad_type"),
                "played_at": played_at or _now(),
            }
            return is_new
