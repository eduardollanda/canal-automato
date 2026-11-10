from __future__ import annotations

from .config import CONTENT_TYPES

KEYWORDS: dict[str, list[str]] = {
    "music": ["music", "musica", "song", "clipe", "oficial audio", "lyrics"],
    "gaming": ["gameplay", "game", "fortnite", "minecraft", "xbox", "playstation"],
    "comedy": ["comedy", "humor", "funny", "standup", "sketch", "comedia"],
    "news": ["news", "noticia", "jornal", "breaking", "headline"],
    "sports": ["sport", "football", "soccer", "futebol", "nba", "highlight"],
    "food": ["recipe", "receita", "food", "cooking", "culinaria", "chef"],
    "tech": ["tech", "review", "unboxing", "iphone", "android", "gadget"],
    "education": ["explained", "tutorial", "learn", "educa", "science", "aula"],
    "lifestyle": ["vlog", "day in the life", "lifestyle", "travel", "viagem"],
    "movie_trailer": ["trailer", "teaser", "official trailer", "filme"],
    "kids": ["kids", "cartoon", "infantil", "nursery", "peppa", "desenho"],
}


def classify_text(title: str = "", description: str = "", channel: str = "") -> str:
    blob = f"{title} {description} {channel}".lower()
    scores: dict[str, int] = {t: 0 for t in CONTENT_TYPES}
    for ctype, words in KEYWORDS.items():
        for w in words:
            if w in blob:
                scores[ctype] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"
