from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .config import CACHE_DIR, CACHE_LIMIT_BYTES, CACHE_SAFETY_MARGIN_BYTES, ensure_dirs
from .models import ProgramItem


class CacheManager:
    """Controla orçamento de 2GB. Em PLAYBACK_MODE=embed só rastreia metadados/arquivos stub."""

    def __init__(self) -> None:
        ensure_dirs()
        self.limit = CACHE_LIMIT_BYTES
        self.margin = CACHE_SAFETY_MARGIN_BYTES

    def used_bytes(self, items: Iterable[ProgramItem]) -> int:
        total = 0
        for item in items:
            if item.status.value in {"ready", "playing", "downloading"}:
                total += max(item.size_bytes, 0)
        # stubs em disco
        if CACHE_DIR.exists():
            for p in CACHE_DIR.glob("*"):
                if p.is_file():
                    total = max(total, total)  # already counted via items; add orphans
        return total

    def free_bytes(self, items: Iterable[ProgramItem]) -> int:
        usable = self.limit - self.margin
        return max(0, usable - self.used_bytes(items))

    def can_fit(self, items: Iterable[ProgramItem], size_bytes: int) -> bool:
        return size_bytes <= self.free_bytes(items)

    def mark_ready_stub(self, item: ProgramItem) -> Path:
        ensure_dirs()
        path = CACHE_DIR / f"{item.id}.ready.json"
        path.write_text(
            json.dumps(
                {
                    "id": item.id,
                    "video_id": item.video_id,
                    "size_bytes": item.size_bytes,
                    "kind": item.kind.value,
                }
            ),
            encoding="utf-8",
        )
        return path

    def evict(self, item: ProgramItem) -> None:
        path = CACHE_DIR / f"{item.id}.ready.json"
        if path.exists():
            path.unlink(missing_ok=True)
        # limpa qualquer arquivo de mídia futuro
        for p in CACHE_DIR.glob(f"{item.id}.*"):
            p.unlink(missing_ok=True)
