from __future__ import annotations

import re

from app.normalize.rules import fold_tr


BLOOM_VERBS = {
    "hatirlama": ["tanimlar", "listeler", "hatirlar", "belirtir", "adlandirir", "sayar"],
    "anlama": ["aciklar", "yorumlar", "ozetler", "ornekler", "tanimlar", "anlatir"],
    "uygulama": ["uygular", "kullanir", "hesaplar", "gosterir", "uyarlar", "calistirir"],
    "analiz": ["analiz eder", "karsilastirir", "ayirt eder", "inceler", "siniflandirir", "ayirir"],
    "degerlendirme": ["degerlendirir", "dogrular", "elestirir", "yargilar", "savunur", "secer"],
    "yaratma": ["tasarlar", "uretir", "gelistirir", "olusturur", "oneri getirir", "kodlar"],
}

HIGHER = {"analiz", "degerlendirme", "yaratma"}

VAGUE = ["bilir", "anlar", "farkinda olur", "bilgi sahibidir"]
ACTIONISH = [
    "uygular",
    "tasarlar",
    "gelistirir",
    "analiz",
    "aciklar",
    "kullanir",
    "olusturur",
    "yazar",
    "degerlendirir",
]


def classify_bloom(text: str) -> str | None:
    folded = fold_tr(text)
    for level, verbs in BLOOM_VERBS.items():
        for verb in verbs:
            if verb in folded:
                return level
    return None


def outcome_quality_flags(text: str) -> list[str]:
    flags = []
    folded = fold_tr(text)
    if len(text.strip()) < 12:
        flags.append("too_short")
    if len(text) > 400:
        flags.append("too_long")
    if any(v in folded for v in VAGUE):
        flags.append("vague_verb")
    if not any(v in folded for v in ACTIONISH):
        flags.append("weak_action_verb")
    if re.search(r"(ogretim elemani|hoca|anlatilir|islenir)", folded):
        flags.append("teacher_activity")
    return flags
