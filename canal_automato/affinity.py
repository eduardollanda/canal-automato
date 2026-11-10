from __future__ import annotations

import random
from collections import deque
from typing import Deque

from .config import (
    AFFINITY_DECAY,
    AFFINITY_LEARNING_RATE,
    BONUS_COMPLETE,
    COMPLETION_THRESHOLD,
    CONTENT_TYPES,
    MAX_TYPE_SHARE,
    MIN_EXPLORE_RATIO,
)


class AffinityEngine:
    def __init__(self) -> None:
        self.weights: dict[str, float] = {t: 1.0 / len(CONTENT_TYPES) for t in CONTENT_TYPES}
        self.view_stats: dict[str, dict[str, float]] = {
            t: {"views": 0, "watched_sec": 0, "completes": 0} for t in CONTENT_TYPES
        }
        self.recent_types: Deque[str] = deque(maxlen=20)

    def load(self, data: dict) -> None:
        if not data:
            return
        weights = data.get("weights") or {}
        for t in CONTENT_TYPES:
            if t in weights:
                self.weights[t] = float(weights[t])
        stats = data.get("view_stats") or {}
        for t, st in stats.items():
            if t in self.view_stats:
                self.view_stats[t].update({k: float(v) for k, v in st.items()})
        recent = data.get("recent_types") or []
        self.recent_types = deque(recent[-20:], maxlen=20)
        self._normalize()

    def dump(self) -> dict:
        return {
            "weights": self.weights,
            "view_stats": self.view_stats,
            "recent_types": list(self.recent_types),
        }

    def _normalize(self) -> None:
        total = sum(max(0.0, v) for v in self.weights.values()) or 1.0
        for t in self.weights:
            self.weights[t] = max(0.0, self.weights[t]) / total

    def record_view(self, content_type: str, watched_ratio: float, watched_sec: float) -> str:
        if content_type not in self.weights:
            content_type = "other"
        signal = max(0.0, min(1.0, watched_ratio))
        completed = watched_ratio >= COMPLETION_THRESHOLD
        if completed:
            signal += BONUS_COMPLETE

        for t in self.weights:
            self.weights[t] *= AFFINITY_DECAY
        self.weights[content_type] += AFFINITY_LEARNING_RATE * signal
        self._normalize()

        st = self.view_stats[content_type]
        st["views"] += 1
        st["watched_sec"] += max(0.0, watched_sec)
        if completed:
            st["completes"] += 1
        self.recent_types.append(content_type)
        return (
            f"affinity↑ {content_type} "
            f"(ratio={watched_ratio:.2f}, peso={self.weights[content_type]:.3f})"
        )

    def _share(self, content_type: str) -> float:
        if not self.recent_types:
            return 0.0
        return sum(1 for t in self.recent_types if t == content_type) / len(self.recent_types)

    def pick_content_type(self) -> tuple[str, str]:
        if random.random() < MIN_EXPLORE_RATIO:
            ctype = random.choice(CONTENT_TYPES)
            return ctype, f"explore → {ctype}"

        items = sorted(self.weights.items(), key=lambda kv: kv[1], reverse=True)
        for ctype, _ in items:
            if self._share(ctype) < MAX_TYPE_SHARE:
                return ctype, f"weighted → {ctype} ({self.weights[ctype]:.3f})"
        ctype = items[0][0]
        return ctype, f"fallback-weighted → {ctype}"
