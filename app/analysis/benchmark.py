from __future__ import annotations

from app.normalize.rules import fold_tr

CS2023 = {
    "AI": ("Artificial Intelligence", "yapay zeka yapay zekâ machine learning makine ogrenmesi nn llm"),
    "AL": ("Algorithmic Foundations", "algoritma veri yapilari complexity karmasiklik"),
    "AR": ("Architecture and Organization", "bilgisayar mimarisi organization processor bellek hiyerarsi"),
    "DM": ("Data Management", "veri tabani veritabani sql nosql data warehouse"),
    "FPL": ("Foundations of Programming Languages", "programlama dilleri compiler derleyici"),
    "GIT": ("Graphics and Interactive Techniques", "bilgisayar grafikleri oyun unity 3d"),
    "HCI": ("Human-Computer Interaction", "insan bilgisayar etkilesimi kullanici arayuzu ux ui"),
    "MSF": ("Mathematical and Statistical Foundations", "ayrik matematik istatistik lineer cebir olasilik"),
    "NC": ("Networking and Communication", "bilgisayar aglari network protokol tcp"),
    "OS": ("Operating Systems", "isletim sistemleri kernel process thread"),
    "PDC": ("Parallel and Distributed Computing", "paralel dagitik concurrent cloud"),
    "SDF": ("Software Development Fundamentals", "programlamaya giris nesne yonelimli yazilim gelistirme temelleri"),
    "SE": ("Software Engineering", "yazilim muhendisligi gereksinim test yazilim mimarisi scrum"),
    "SEC": ("Security", "guvenlik kriptografi siber bilgi guvenligi"),
    "SEP": ("Society, Ethics, and the Profession", "etik meslek hukuk toplum"),
    "SF": ("Systems Fundamentals", "sistem temelleri digital mantik gomulu"),
    "SPD": ("Specialized Platform Development", "mobil web android ios platform"),
}

SEEK = {
    "CMP": ("Computing Essentials", "programlama veri yapilari isletim sistemi ag"),
    "FND": ("Mathematical and Engineering Fundamentals", "matematik fizik olasilik"),
    "PRF": ("Professional Practice", "etik iletisim takim proje yonetimi"),
    "MAA": ("Software Modeling and Analysis", "modelleme uml analiz gereksinim"),
    "DES": ("Software Design", "yazilim tasarimi mimari desen pattern"),
    "VAV": ("Software Verification and Validation", "test dogrulama kalite"),
    "PRO": ("Software Process", "surec cmmi agile scrum"),
    "QUA": ("Software Quality", "kalite metrik olcum"),
    "MGT": ("Software Management", "proje yonetimi maliyet risk"),
}


def classify_text(text: str, framework: dict[str, tuple[str, str]]) -> tuple[str | None, float]:
    folded = fold_tr(text)
    best_code, best_score = None, 0.0
    tokens = set(folded.split())
    for code, (_name, kws) in framework.items():
        keys = set(fold_tr(kws).split())
        overlap = len(tokens & keys)
        score = overlap / max(1, len(keys) * 0.15)
        # also substring boost
        hits = sum(1 for k in keys if k in folded)
        score = max(score, hits / 8)
        if score > best_score:
            best_code, best_score = code, min(score, 1.0)
    if best_score < 0.12:
        return None, 0.0
    return best_code, round(best_score, 3)


def classify_course(title: str, description: str = "", outcomes: str = "", code: str = "") -> tuple[str | None, float, str]:
    parts = [
        (title, 0.30),
        (description, 0.35),
        (outcomes, 0.30),
        (code, 0.05),
    ]
    scores: dict[str, float] = {}
    for text, weight in parts:
        if not text:
            continue
        area, conf = classify_text(text, CS2023)
        if area:
            scores[area] = scores.get(area, 0) + conf * weight
    if not scores:
        return None, 0.0, "CS2023"
    best = max(scores, key=scores.get)
    return best, round(scores[best], 3), "CS2023"
