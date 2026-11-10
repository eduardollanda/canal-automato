from __future__ import annotations

import logging
import random
from typing import Any, Optional

from .config import (
    AD_DURATION_WINDOWS,
    AD_TYPE_QUERIES,
    CONTENT_TYPE_QUERIES,
    CONTENT_TYPES,
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


def _content_ok(item: dict[str, Any], exclude_ids: set[str]) -> bool:
    if item["video_id"] in exclude_ids:
        return False
    dur = item.get("duration") or 0
    if dur and dur < 20:
        return False
    if dur and dur > 20 * 60:
        return False
    return True


def _pack_content(item: dict[str, Any], content_type: str, query: str, *, expanded: bool = False) -> dict[str, Any]:
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
        "search_expanded": expanded,
    }


def _seed_content(content_type: str, exclude_ids: set[str]) -> Optional[dict[str, Any]]:
    seeds = [s for s in FALLBACK_SEEDS if s["video_id"] not in exclude_ids]
    if not seeds:
        return None
    typed = [s for s in seeds if s["content_type"] == content_type] or seeds
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


def _last_resort_seed(content_type: str) -> dict[str, Any]:
    """Último recurso documentado: só quando não há nenhuma alternativa inédita."""
    seed = random.choice(FALLBACK_SEEDS)
    return {
        "video_id": seed["video_id"],
        "title": seed["title"],
        "duration": seed["duration"],
        "content_type": content_type if seed["content_type"] == "other" else seed["content_type"],
        "size_bytes": estimate_size_bytes(seed["duration"]),
        "matched_query": "fallback-seed-repeat",
        "is_fallback": True,
        "is_repeat_last_resort": True,
    }


def find_content(content_type: str, exclude_ids: set[str] | None = None) -> Optional[dict[str, Any]]:
    """
    Política anti-repetição (nunca preferir repetir se houver alternativa):
    1. Busca com queries do tipo pedido (limit 6).
    2. Expande: todas as queries do tipo + limit maior (12).
    3. Tenta outros content_types (ordem embaralhada).
    4. Seed de fallback ainda não visto.
    5. Só então last-resort com seed já visto (continuidade do ar).
    """
    exclude_ids = set(exclude_ids or set())
    queries = list(CONTENT_TYPE_QUERIES.get(content_type, CONTENT_TYPE_QUERIES["other"]))
    random.shuffle(queries)

    # 1) busca normal
    for query in queries[:2]:
        for item in _yt_search(query, limit=6):
            if _content_ok(item, exclude_ids):
                return _pack_content(item, content_type, query)

    # 2) expandir busca do mesmo tipo
    logger.info("find_content: expandindo busca para tipo=%s (sem novidade)", content_type)
    for query in queries:
        for item in _yt_search(query, limit=12):
            if _content_ok(item, exclude_ids):
                return _pack_content(item, content_type, query, expanded=True)

    # 3) tentar outros tipos
    other_types = [t for t in CONTENT_TYPES if t != content_type]
    random.shuffle(other_types)
    for alt_type in other_types:
        alt_queries = list(CONTENT_TYPE_QUERIES.get(alt_type, []))
        if not alt_queries:
            continue
        query = random.choice(alt_queries)
        for item in _yt_search(query, limit=8):
            if _content_ok(item, exclude_ids):
                logger.info("find_content: novidade via tipo alternativo %s (pedido=%s)", alt_type, content_type)
                return _pack_content(item, alt_type, query, expanded=True)

    # 4) seed inédito
    seed = _seed_content(content_type, exclude_ids)
    if seed:
        logger.warning("find_content: usando seed inédito (pedido=%s)", content_type)
        return seed

    # 5) last resort (repetição só para não parar o canal)
    logger.error("find_content: sem novidade — last-resort com seed já visto")
    return _last_resort_seed(content_type)


def _ad_score(item: dict[str, Any], target: float, lo: float, hi: float) -> float:
    dur = item.get("duration") or 0
    if dur <= 0 or not (lo <= dur <= hi):
        return -1.0
    proximity = 1.0 - min(abs(dur - target) / max(target, 1), 1.0)
    size_score = 1.0 if (item.get("filesize_approx") or 0) < 80 * 1024 * 1024 else 0.5
    return proximity * 0.75 + size_score * 0.25


def find_ad(ad_type: str, exclude_ids: set[str] | None = None) -> Optional[dict[str, Any]]:
    """
    Política anti-repetição de ads:
    1. Queries do tipo com filtro de duração.
    2. Expandir limit e todas as queries.
    3. Tentar tipos coringa (generic_brand, promo_house) se diferentes.
    4. Fallback curto inédito se possível; senão last-resort documentado.
    """
    exclude_ids = set(exclude_ids or set())
    target, lo, hi = AD_DURATION_WINDOWS.get(ad_type, (30, 20, 45))
    queries = list(AD_TYPE_QUERIES.get(ad_type, AD_TYPE_QUERIES["generic_brand"]))

    def search(type_key: str, qlist: list[str], limit: int) -> Optional[dict[str, Any]]:
        best = None
        best_score = -1.0
        used_query = qlist[0] if qlist else type_key
        for query in qlist:
            used_query = query
            for item in _yt_search(query, limit=limit):
                if item["video_id"] in exclude_ids:
                    continue
                score = _ad_score(item, target, lo, hi)
                if score > best_score:
                    best_score = score
                    best = item
        if not best:
            return None
        size = best["filesize_approx"] or estimate_size_bytes(best["duration"])
        return {
            **best,
            "ad_type": type_key,
            "target_duration_sec": target,
            "size_bytes": size,
            "matched_query": used_query,
            "match_score": round(best_score, 3),
        }

    found = search(ad_type, queries, limit=8)
    if found:
        return found

    logger.info("find_ad: expandindo busca tipo=%s", ad_type)
    found = search(ad_type, queries, limit=15)
    if found:
        found["search_expanded"] = True
        return found

    for alt in ("generic_brand", "promo_house"):
        if alt == ad_type:
            continue
        alt_queries = list(AD_TYPE_QUERIES.get(alt, []))
        alt_target, alt_lo, alt_hi = AD_DURATION_WINDOWS.get(alt, (30, 20, 45))
        # reusa janela do tipo pedido se o coringa for genérico
        best = None
        best_score = -1.0
        used_query = alt_queries[0] if alt_queries else alt
        for query in alt_queries:
            used_query = query
            for item in _yt_search(query, limit=10):
                if item["video_id"] in exclude_ids:
                    continue
                score = _ad_score(item, target, lo, hi)
                if score < 0:
                    score = _ad_score(item, alt_target, alt_lo, alt_hi)
                if score > best_score:
                    best_score = score
                    best = item
        if best:
            logger.info("find_ad: novidade via tipo alternativo %s (pedido=%s)", alt, ad_type)
            size = best["filesize_approx"] or estimate_size_bytes(best["duration"])
            return {
                **best,
                "ad_type": ad_type,
                "target_duration_sec": target,
                "size_bytes": size,
                "matched_query": used_query,
                "match_score": round(best_score, 3),
                "search_expanded": True,
                "alt_ad_type": alt,
            }

    # fallback curto conhecido, só se ainda não visto
    fallback_id = "jNQXAC9IVRw"
    if fallback_id not in exclude_ids:
        return {
            "video_id": fallback_id,
            "title": f"Ad fallback ({ad_type})",
            "duration": 19,
            "ad_type": ad_type,
            "target_duration_sec": target,
            "size_bytes": estimate_size_bytes(19),
            "matched_query": "ad-fallback",
            "match_score": 0.1,
            "is_fallback": True,
        }

    # last resort: repetir fallback para não furar o break (documentado)
    logger.error("find_ad: sem novidade — last-resort com ad fallback já visto")
    return {
        "video_id": fallback_id,
        "title": f"Ad fallback repeat ({ad_type})",
        "duration": 19,
        "ad_type": ad_type,
        "target_duration_sec": target,
        "size_bytes": estimate_size_bytes(19),
        "matched_query": "ad-fallback-repeat",
        "match_score": 0.05,
        "is_fallback": True,
        "is_repeat_last_resort": True,
    }
