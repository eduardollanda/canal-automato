from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ItemKind(str, Enum):
    content = "content"
    ad = "ad"


class ItemStatus(str, Enum):
    planned = "planned"
    matching = "matching"
    downloading = "downloading"
    ready = "ready"
    playing = "playing"
    played = "played"
    deleted = "deleted"
    failed = "failed"


class ProgramItem(BaseModel):
    id: str
    kind: ItemKind
    video_id: str = ""
    title: str = ""
    duration_sec: float = 0
    size_bytes: int = 0
    status: ItemStatus = ItemStatus.planned
    content_type: Optional[str] = None
    ad_type: Optional[str] = None
    target_duration_sec: Optional[float] = None
    matched_query: Optional[str] = None
    match_score: Optional[float] = None
    watched_sec: float = 0
    watched_ratio: float = 0
    completed: bool = False
    is_fallback: bool = False

    def public_dict(self) -> dict[str, Any]:
        return self.model_dump()


class EngineSnapshot(BaseModel):
    channel_name: str
    playback_mode: str
    current: Optional[ProgramItem] = None
    queue: list[ProgramItem] = Field(default_factory=list)
    affinity: dict[str, float] = Field(default_factory=dict)
    view_stats: dict[str, dict[str, float]] = Field(default_factory=dict)
    cache_used_bytes: int = 0
    cache_limit_bytes: int = 0
    cache_pct: float = 0
    recent_as_run: list[dict[str, Any]] = Field(default_factory=list)
    algorithm_log: list[str] = Field(default_factory=list)
    content_since_break: int = 0
    status: str = "starting"
