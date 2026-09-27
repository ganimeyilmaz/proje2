import re
import unicodedata


_EMPTY = {"", "-", "—", "n/a", "na", "yok", "belirtilmemiş", "belirtilmemis", "none", "null"}

_REQUIRED = {"z", "zorunlu", "required", "c", "compulsory", "must", "core"}
_ELECTIVE = {"s", "seçmeli", "secmeli", "elective", "e", "optional"}

_ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8"}


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned.lower() in _EMPTY:
        return None
    return cleaned or None


def fold_tr(text: str) -> str:
    text = text.translate(str.maketrans("İI", "iı"))
    text = text.lower()
    text = text.translate(str.maketrans("ğüşöçı", "gusoci"))
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def parse_ects(value: str | None) -> float | None:
    value = empty_to_none(value)
    if value is None:
        return None
    match = re.search(r"(\d+(?:[.,]\d+)?)", value.replace(" ", ""))
    if not match:
        return None
    number = float(match.group(1).replace(",", "."))
    if number <= 0 or number > 40:
        return None
    return number


def normalize_course_type(value: str | None) -> str | None:
    value = empty_to_none(value)
    if value is None:
        return None
    token = fold_tr(value).strip()
    if token in _REQUIRED:
        return "REQUIRED"
    if token in _ELECTIVE:
        return "ELECTIVE"
    if "zorun" in token or "requir" in token:
        return "REQUIRED"
    if "secmel" in token or "elect" in token:
        return "ELECTIVE"
    return None


def normalize_semester(value: str | None) -> int | None:
    value = empty_to_none(value)
    if value is None:
        return None
    folded = fold_tr(value)
    match = re.search(r"(\d+)", folded)
    if match:
        n = int(match.group(1))
        return n if 1 <= n <= 12 else None
    for roman, n in _ROMAN.items():
        if re.search(rf"\b{roman}\b", folded):
            return int(n)
    if "guz" in folded or "fall" in folded:
        return 1
    if "bahar" in folded or "spring" in folded:
        return 2
    return None


def normalize_language(value: str | None) -> str | None:
    value = empty_to_none(value)
    if value is None:
        return None
    folded = fold_tr(value)
    if folded.startswith("tr") or "turk" in folded:
        return "tr"
    if folded.startswith("en") or "ingiliz" in folded or "english" in folded:
        return "en"
    return folded[:8]


_TITLE_STOP = (
    r"\b(introduction to|intro to|giris|temelleri|temel|sistemleri|sistemi|"
    r"principles of|and|ve|of|the)\b"
)


def normalize_title(value: str | None) -> str | None:
    value = empty_to_none(value)
    if value is None:
        return None
    text = fold_tr(value)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\b(i{1,3}|iv|v|vi{0,3}|1|2|3|4)\b", " ", text)
    text = re.sub(_TITLE_STOP, " ", text)
    text = text.replace("veri tabani", "veritabani")
    text = text.replace("yapay zeka", "yapayzeka")
    text = text.replace("isletim sistem", "isletimsistem")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None
