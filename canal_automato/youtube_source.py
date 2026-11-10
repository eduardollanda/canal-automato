from __future__ import annotations

import logging
import random
from typing import Any, Optional

from .config import (
    AD_DURATION_WINDOWS,
    AD_TYPE_QUERIES,
    CONTENT_TYPE_QUERIES,
    FALLBACK_SEEDS,
)
from .taxonomy import classify_text

logger = logging.getLogger(__name__)


def _yt_search(query: str, limit: int = 8) -> list[dict[str, Any]]:
    try:
        import yt_dlp
    except Exception as exc:  # pragma: no cover
        logger.warning("yt-dlp indisponivel: %s", exc)
        return []

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "nocheckcertificate": True,
    }
    results: list[dict[str, Any]] = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            for e in info.get("entries") or []:
                if not e:
                    continue
                vid = e.get("id")
                if not vid:
                    continue
                duration = float(e.get("duration") or 0)
                title = e.get("title") or ""
                results.append(
                    {
                        "video_id": vid,
                        "title": title,
                        "duration": duration,
                        "filesize_approx": int(e.get("filesize_approx") or e.get("filesize") or 0),
                        "channel": e.get("channel") or e.get("uploader") or "",
                        "description": (e.get("description") or "")[:500],
                        "query": query,
                    }
                )
    except Exception as exc:
        logger.warning("busca youtube falhou (%s): %s", query, exc)
    return results


def estimate_size_bytes(duration_sec: float) -> int:
    # ~0.4 MB/s em 360p aproximado — usado para orçamento lógico de 2GB.
    return int(max(duration_sec, 15) * 0.4 * 1024 * 1024)


def _seed_content(content_type: str, exclude_ids: set[str]) -> dict[str, Any]:
    seeds = [s for s in FALLBACK_SEEDS if s["video_id"] not in exclude_ids]
    typed = [s for s in seeds if s["content_type"] == content_type] or seeds or FALLBACK_SEEDS
    seed = random.choice(typed)
    return {
        "video_id": seed["video_id"],
        "title": seed["title"],
        "duration": seed["duration"],
        "content_type": content_type if seed["content_type"] == "other" else seed["content_type"],
        "size_bytes": estimate_size_bytes(seed["duration"]),
        "matched_query": "fallback-seed",
        "is_fallback": True,
    }


def find_content(content_type: str, exclude_ids: set[str] | None = None) -> Optional[dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    queries = CONTENT_TYPE_QUERIES.get(content_type, CONTENT_TYPE_QUERIES["other"])
    query = random.choice(queries)
    try:
        for item in _yt_search(query, limit=6):
            if item["video_id"] in exclude_ids:
                continue
            if item["duration"] and item["duration"] < 20:
                continue
            if item["duration"] and item["duration"] > 20 * 60:
                continue
            detected = classify_text(item["title"], item["description"], item["channel"])
            if detected == "other":
                detected = content_type
            size = item["filesize_approx"] or estimate_size_bytes(item["duration"] or 180)
            return {
                **item,
                "content_type": content_type,
                "detected_type": detected,
                "size_bytes": size,
                "matched_query": query,
            }
    except Exception as exc:
        logger.warning("find_content fallback seed: %s", exc)
    return _seed_content(content_type, exclude_ids)


def find_ad(ad_type: str, exclude_ids: set[str] | None = None) -> Optional[dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    target, lo, hi = AD_DURATION_WINDOWS.get(ad_type, (30, 20, 45))
    queries = AD_TYPE_QUERIES.get(ad_type, AD_TYPE_QUERIES["generic_brand"])
    best = None
    best_score = -1.0
    used_query = queries[0]

    for query in queries:
        used_query = query
        for item in _yt_search(query, limit=8):
            if item["video_id"] in exclude_ids:
                continue
            dur = item["duration"] or 0
            if dur <= 0:
                continue
            if not (lo <= dur <= hi):
                continue
            proximity = 1.0 - min(abs(dur - target) / max(target, 1), 1.0)
            size_score = 1.0 if (item["filesize_approx"] or 0) < 80 * 1024 * 1024 else 0.5
            score = proximity * 0.75 + size_score * 0.25
            if score > best_score:
                best_score = score
                best = item

    if best:
        size = best["filesize_approx"] or estimate_size_bytes(best["duration"])
        return {
            **best,
            "ad_type": ad_type,
            "target_duration_sec": target,
            "size_bytes": size,
            "matched_query": used_query,
            "match_score": round(best_score, 3),
        }

    # Fallback curto conhecido
    return {
        "video_id": "jNQXAC9IVRw",
        "title": f"Ad fallback ({ad_type})",
        "duration": 19,
        "ad_type": ad_type,
        "target_duration_sec": target,
        "size_bytes": estimate_size_bytes(19),
        "matched_query": "ad-fallback",
        "match_score": 0.1,
        "is_fallback": True,
    }
