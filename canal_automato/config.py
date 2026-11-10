from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
CACHE_DIR = Path(os.getenv("CACHE_DIR", DATA_DIR / "cache"))
STATE_PATH = Path(os.getenv("STATE_PATH", DATA_DIR / "state.json"))
HISTORY_PATH = Path(os.getenv("HISTORY_PATH", DATA_DIR / "video_history.json"))
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
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "frapfel TV")

# Editorial: futebol brasileiro (Brasileirão, clubes, seleções, gols, análises).
CONTENT_TYPES = [
    "gols",
    "melhores_momentos",
    "analise",
    "entrevista",
    "bastidores",
    "classico",
    "brasileirao",
    "copa",
    "selecao",
    "curiosidade",
    "other",
]

CONTENT_TYPE_QUERIES = {
    "gols": [
        "gols brasileirão 2024",
        "melhores gols futebol brasileiro",
        "gols flamengo palmeiras corinthians",
    ],
    "melhores_momentos": [
        "melhores momentos brasileirão",
        "highlights futebol brasil",
        "melhores momentos campeonato brasileiro",
    ],
    "analise": [
        "análise tática futebol brasileiro",
        "comentários pós jogo brasileirão",
        "análise rodada campeonato brasileiro",
    ],
    "entrevista": [
        "entrevista jogador futebol brasileiro",
        "coletiva técnico brasileirão",
        "entrevista craque futebol brasil",
    ],
    "bastidores": [
        "bastidores clube futebol brasil",
        "making of futebol brasileiro",
        "bastidores seleção brasileira",
    ],
    "classico": [
        "clássico futebol brasileiro gols",
        "flamengo fluminense clássico",
        "corinthians palmeiras clássico",
        "grêmio internacional clássico",
    ],
    "brasileirao": [
        "campeonato brasileiro série a",
        "brasileirão rodada resumo",
        "tabela brasileirão análise",
    ],
    "copa": [
        "copa do brasil gols",
        "copa do brasil melhores momentos",
        "final copa do brasil",
    ],
    "selecao": [
        "seleção brasileira gols",
        "brasil seleção melhores momentos",
        "amigável seleção brasileira",
    ],
    "curiosidade": [
        "curiosidades futebol brasileiro",
        "história clubes brasileiros",
        "documentário futebol brasil",
    ],
    "other": [
        "futebol brasileiro youtube",
        "esporte futebol brasil highlights",
    ],
}

AD_TYPE_QUERIES = {
    "spot_15": ["15 second commercial", "propaganda 15 segundos"],
    "spot_30": ["30 second tv commercial", "propaganda 30 segundos futebol"],
    "spot_60": ["60 second commercial", "filme publicitario 1 minuto"],
    "retail": ["sportswear commercial", "propaganda loja esporte nike adidas"],
    "food_beverage": ["beer commercial soccer", "propaganda cerveja futebol"],
    "tech": ["tech gadget commercial", "propaganda celular tecnologia"],
    "auto": ["car commercial 30 seconds", "propaganda carro"],
    "finance": ["bank commercial sports", "propaganda banco patrocinio futebol"],
    "beauty": ["beauty product ad", "propaganda cosmetico"],
    "trailer": ["sports documentary trailer", "trailer documentario futebol"],
    "event": ["football match promo", "propaganda jogo futebol ingresso"],
    "public_service": ["public service announcement", "campanha utilidade publica"],
    "promo_house": ["tv sports channel bump promo", "vinheta canal esporte futebol"],
    "generic_brand": ["brand commercial sports", "propaganda marca esporte"],
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
    "gols": ["event", "spot_30", "food_beverage"],
    "melhores_momentos": ["event", "retail", "spot_30"],
    "analise": ["finance", "spot_30", "generic_brand"],
    "entrevista": ["spot_30", "retail", "promo_house"],
    "bastidores": ["promo_house", "event", "spot_30"],
    "classico": ["event", "food_beverage", "retail"],
    "brasileirao": ["event", "finance", "spot_30"],
    "copa": ["event", "trailer", "spot_30"],
    "selecao": ["event", "retail", "food_beverage"],
    "curiosidade": ["trailer", "promo_house", "generic_brand"],
    "other": ["event", "spot_30", "generic_brand"],
}

# Seeds estáveis para bootstrap quando a busca YouTube falha.
FALLBACK_SEEDS = [
    {"video_id": "Rk6_hdRtJOE", "title": "Football Skills", "duration": 240, "content_type": "melhores_momentos"},
    {"video_id": "jNQXAC9IVRw", "title": "Me at the zoo (fill curto)", "duration": 19, "content_type": "other"},
    {"video_id": "aqz-KE-bpKQ", "title": "Big Buck Bunny (fill)", "duration": 596, "content_type": "other"},
    {"video_id": "LXb3EKWsInQ", "title": "Costa Rica in 4K (fill)", "duration": 303, "content_type": "curiosidade"},
    {"video_id": "ScMzIvxBSi4", "title": "Relaxing Music (fill)", "duration": 180, "content_type": "bastidores"},
]


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
