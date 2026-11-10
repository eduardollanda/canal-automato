from __future__ import annotations

from .config import CONTENT_TYPES

KEYWORDS: dict[str, list[str]] = {
    "gols": ["gol", "gols", "goal", "hat-trick", "hat trick", "placa"],
    "melhores_momentos": [
        "melhores momentos",
        "highlights",
        "resumo",
        "lances",
        "melhor lance",
    ],
    "analise": [
        "análise",
        "analise",
        "tática",
        "tatica",
        "comentário",
        "comentario",
        "pós-jogo",
        "pos-jogo",
        "pós jogo",
    ],
    "entrevista": [
        "entrevista",
        "coletiva",
        "entrevista exclusiva",
        "bate-papo",
        "talk",
    ],
    "bastidores": [
        "bastidores",
        "making of",
        "nos bastidores",
        "treino",
        "concentração",
        "concentracao",
    ],
    "classico": [
        "clássico",
        "classico",
        "derby",
        "flamengo fluminense",
        "corinthians palmeiras",
        "grêmio internacional",
        "gremio internacional",
        "atlético mineiro cruzeiro",
        "atletico mineiro cruzeiro",
        "são paulo corinthians",
        "sao paulo corinthians",
    ],
    "brasileirao": [
        "brasileirão",
        "brasileirao",
        "campeonato brasileiro",
        "série a",
        "serie a",
        "rodada",
    ],
    "copa": [
        "copa do brasil",
        "copa brasil",
        "libertadores",
        "sul-americana",
        "sulamericana",
    ],
    "selecao": [
        "seleção brasileira",
        "selecao brasileira",
        "brasil x",
        "canarinho",
        "copa do mundo",
        "amigável",
        "amigavel",
    ],
    "curiosidade": [
        "curiosidade",
        "história",
        "historia",
        "documentário",
        "documentario",
        "retrospectiva",
        "arquivo",
    ],
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
