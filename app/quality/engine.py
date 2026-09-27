from __future__ import annotations

QUALITY_WEIGHTS = {
    "curriculum_present": 20,
    "identity_complete": 15,
    "ects": 15,
    "course_type": 10,
    "content": 10,
    "learning_outcomes": 20,
    "source_url": 10,
}


def evaluate_curriculum(curriculum, courses=None) -> tuple[list[dict], float]:
    issues: list[dict] = []
    if courses is None:
        courses = [c for s in curriculum.semesters for c in s.courses]
    n = len(courses) or 1

    if not courses:
        issues.append(
            {
                "code": "NO_COURSES",
                "severity": "critical",
                "description": "Müfredatta ders bulunamadı.",
            }
        )

    identity_ok = sum(1 for c in courses if (c.code or c.name_tr) and c.semester_id) / n
    ects_ok = sum(1 for c in courses if c.ects) / n
    type_ok = sum(1 for c in courses if c.course_type) / n
    content_ok = sum(
        1
        for c in courses
        if c.content and (c.content.description or c.content.weekly_content)
    ) / n
    lo_ok = sum(1 for c in courses if c.outcomes) / n
    source_ok = 1.0 if curriculum.source_url else 0.0
    present = 1.0 if courses else 0.0

    if identity_ok < 0.8:
        issues.append(
            {
                "code": "IDENTITY_GAPS",
                "severity": "high",
                "description": "Ders kodu/adı/dönem bütünlüğü düşük.",
            }
        )
    if ects_ok < 0.7:
        issues.append(
            {
                "code": "ECTS_MISSING",
                "severity": "high",
                "description": "AKTS bilgisi birçok derste yok.",
            }
        )
    if lo_ok < 0.5:
        issues.append(
            {
                "code": "LO_COVERAGE_LOW",
                "severity": "high",
                "description": "Öğrenme çıktısı kapsamı düşük.",
            }
        )
    if not curriculum.source_url:
        issues.append(
            {
                "code": "NO_SOURCE_URL",
                "severity": "critical",
                "description": "Kaynak URL yok.",
            }
        )

    ects_sum = sum(c.ects or 0 for c in courses)
    if curriculum.total_ects and ects_sum and abs(curriculum.total_ects - ects_sum) > 10:
        issues.append(
            {
                "code": "ECTS_MISMATCH",
                "severity": "high",
                "description": f"Müfredat AKTS {curriculum.total_ects} ile ders toplamı {ects_sum} uyumsuz.",
            }
        )

    score = (
        present * QUALITY_WEIGHTS["curriculum_present"]
        + identity_ok * QUALITY_WEIGHTS["identity_complete"]
        + ects_ok * QUALITY_WEIGHTS["ects"]
        + type_ok * QUALITY_WEIGHTS["course_type"]
        + content_ok * QUALITY_WEIGHTS["content"]
        + lo_ok * QUALITY_WEIGHTS["learning_outcomes"]
        + source_ok * QUALITY_WEIGHTS["source_url"]
    )
    return issues, round(score, 1)
