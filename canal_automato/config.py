from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
CACHE_DIR = Path(os.getenv("CACHE_DIR", DATA_DIR / "cache"))
STATE_PATH = Path(os.getenv("STATE_PATH", DATA_DIR / "state.json"))
ASSETS_DIR = ROOT / "assets"
LOGO_PATH = ASSETS_DIR / "logo.jpg"

CACHE_LIMIT_BYTES = int(os.getenv("CACHE_LIMIT_BYTES", str(2 * 1024 * 1024 * 1024)))
CACHE_SAFETY_MARGIN_BYTES = int(os.getenv("CACHE_SAFETY_MARGIN_BYTES", str(150 * 1024 * 1024)))
MAX_READY_AHEAD = int(os.getenv("MAX_READY_AHEAD", "1"))
PREFETCH_MARGIN_SEC = int(os.getenv("PREFETCH_MARGIN_SEC", "20"))

ADS_EVERY_N_CONTENT = int(os.getenv("ADS_EVERY_N_CONTENT", "1"))
BREAK_BUDGET_SEC = int(os.getenv("BREAK_BUDGET_SEC", "45"))

AFFINITY_LEARNING_RATE = float(os.getenv("AFFINITY_LEARNING_RATE", "0.25"))
AFFINITY_DECAY = float(os.getenv("AFFINITY_DECAY", "0.995"))
COMPLETION_THRESHOLD = float(os.getenv("COMPLETION_THRESHOLD", "0.9"))
BONUS_COMPLETE = float(os.getenv("BONUS_COMPLETE", "0.5"))
MIN_EXPLORE_RATIO = float(os.getenv("MIN_EXPLORE_RATIO", "0.2"))
MAX_TYPE_SHARE = float(os.getenv("MAX_TYPE_SHARE", "0.55"))

# embed = YouTube no browser (sem baixar vídeo no disco). Ideal para Railway.
PLAYBACK_MODE = os.getenv("PLAYBACK_MODE", "embed")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "Canal Automato")

CONTENT_TYPES = [
    "music",
    "gaming",
    "comedy",
    "news",
    "sports",
    "food",
    "tech",
    "education",
    "lifestyle",
    "movie_trailer",
    "kids",
    "other",
]

CONTENT_TYPE_QUERIES = {
    "music": ["official music video", "clipe oficial musica"],
    "gaming": ["gameplay highlights", "gameplay ao vivo curto"],
    "comedy": ["standup comedy short", "sketch comedy"],
    "news": ["world news today", "noticias do dia"],
    "sports": ["sports highlights", "melhores momentos futebol"],
    "food": ["easy recipe short", "receita rapida"],
    "tech": ["tech review short", "unboxing tecnologia"],
    "education": ["science explained short", "tutorial educativo"],
    "lifestyle": ["day in the life vlog", "lifestyle vlog"],
    "movie_trailer": ["official movie trailer", "trailer oficial filme"],
    "kids": ["kids cartoon short", "desenho infantil curto"],
    "other": ["interesting short video", "video interessante curto"],
}

AD_TYPE_QUERIES = {
    "spot_15": ["15 second commercial", "propaganda 15 segundos"],
    "spot_30": ["30 second tv commercial", "propaganda 30 segundos"],
    "spot_60": ["60 second commercial", "filme publicitario 1 minuto"],
    "retail": ["retail store commercial", "propaganda oferta loja"],
    "food_beverage": ["food commercial 30 seconds", "propaganda comida bebida"],
    "tech": ["tech gadget commercial", "propaganda celular tecnologia"],
    "auto": ["car commercial 30 seconds", "propaganda carro"],
    "finance": ["bank commercial", "propaganda banco cartao"],
    "beauty": ["beauty product ad", "propaganda cosmetico"],
    "trailer": ["movie trailer 60 seconds", "trailer oficial curto"],
    "event": ["event promo commercial", "propaganda show evento"],
    "public_service": ["public service announcement", "campanha utilidade publica"],
    "promo_house": ["tv channel bump promo", "vinheta canal tv"],
    "generic_brand": ["brand commercial ad", "propaganda marca"],
}

AD_DURATION_WINDOWS = {
    "spot_15": (15, 12, 18),
    "spot_30": (30, 25, 35),
    "spot_60": (60, 50, 70),
    "retail": (30, 20, 40),
    "food_beverage": (30, 20, 40),
    "tech": (30, 20, 40),
    "auto": (30, 25, 65),
    "finance": (30, 20, 40),
    "beauty": (20, 12, 35),
    "trailer": (60, 30, 90),
    "event": (20, 12, 35),
    "public_service": (30, 20, 40),
    "promo_house": (15, 8, 25),
    "generic_brand": (20, 12, 35),
}

CONTENT_AD_BIAS = {
    "food": ["food_beverage", "retail"],
    "tech": ["tech", "trailer"],
    "gaming": ["tech", "trailer", "event"],
    "sports": ["event", "retail", "spot_30"],
    "music": ["event", "spot_30", "generic_brand"],
    "movie_trailer": ["trailer", "spot_30"],
    "kids": ["promo_house", "generic_brand"],
}

# Seeds estáveis (Creative Commons / oficiais comuns) para bootstrap offline de busca.
FALLBACK_SEEDS = [
    {"video_id": "jNQXAC9IVRw", "title": "Me at the zoo", "duration": 19, "content_type": "other"},
    {"video_id": "aqz-KE-bpKQ", "title": "Big Buck Bunny", "duration": 596, "content_type": "kids"},
    {"video_id": "LXb3EKWsInQ", "title": "Costa Rica in 4K", "duration": 303, "content_type": "lifestyle"},
    {"video_id": "ScMzIvxBSi4", "title": "Relaxing Music", "duration": 180, "content_type": "music"},
    {"video_id": "Rk6_hdRtJOE", "title": "Football Skills", "duration": 240, "content_type": "sports"},
]


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
