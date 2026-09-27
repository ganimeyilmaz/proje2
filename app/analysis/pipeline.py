from __future__ import annotations

from sqlalchemy.orm import Session

from app.analysis.benchmark import classify_course
from app.analysis.bloom import classify_bloom, outcome_quality_flags
from app.analysis.similarity import compare_title_sets, tfidf_cosine
from app.models import AnalysisResult, Course, CurriculumVersion, Program, Semester


def courses_of(curriculum: CurriculumVersion, db: Session | None = None) -> list[Course]:
    if db is not None and curriculum.id:
        return (
            db.query(Course)
            .join(Semester)
            .filter(Semester.curriculum_version_id == curriculum.id)
            .all()
        )
    return [c for s in curriculum.semesters for c in s.courses]


def annotate_courses(db: Session, curriculum: CurriculumVersion) -> None:
    for course in courses_of(curriculum, db):
        desc = ""
        if course.content:
            desc = " ".join(
                filter(
                    None,
                    [
                        course.content.purpose,
                        course.content.description,
                        course.content.weekly_content,
                    ],
                )
            )
        outcomes = " ".join(o.outcome_text for o in course.outcomes)
        area, conf, _ = classify_course(
            course.name_tr or course.name_en or "",
            desc,
            outcomes,
            course.code or "",
        )
        course.topic_area = area
        course.topic_confidence = conf
        for outcome in course.outcomes:
            outcome.bloom_level = classify_bloom(outcome.outcome_text)
            flags = outcome_quality_flags(outcome.outcome_text)
            outcome.quality_flags = ",".join(flags) if flags else None
    db.commit()


def compare_programs(db: Session, program_a_id: int, program_b_id: int) -> dict:
    ca = _latest(db, program_a_id)
    cb = _latest(db, program_b_id)
    if not ca or not cb:
        return {"error": "Her iki program için müfredat yok."}
    courses_a = courses_of(ca, db)
    courses_b = courses_of(cb, db)
    titles_a = {c.normalized_title for c in courses_a if c.normalized_title}
    titles_b = {c.normalized_title for c in courses_b if c.normalized_title}
    title_cmp = compare_title_sets(titles_a, titles_b)
    texts_a = [_course_blob(c) for c in courses_a]
    texts_b = [_course_blob(c) for c in courses_b]
    cosine = tfidf_cosine(texts_a, texts_b)
    result = {
        "program_a": program_a_id,
        "program_b": program_b_id,
        "jaccard": title_cmp["jaccard"],
        "tfidf_cosine": cosine,
        "shared": title_cmp["shared"],
        "only_a": title_cmp["only_a"],
        "only_b": title_cmp["only_b"],
        "ects_a": sum(c.ects or 0 for c in courses_a),
        "ects_b": sum(c.ects or 0 for c in courses_b),
        "lo_a": sum(len(c.outcomes) for c in courses_a),
        "lo_b": sum(len(c.outcomes) for c in courses_b),
    }
    db.add(
        AnalysisResult(
            entity_a=str(program_a_id),
            entity_b=str(program_b_id),
            analysis_type="program_compare",
            metric_name="weighted_similarity",
            metric_value=round(0.4 * title_cmp["jaccard"] + 0.6 * cosine, 4),
            detail=str({k: result[k] for k in ("jaccard", "tfidf_cosine")}),
        )
    )
    db.commit()
    return result


def _latest(db: Session, program_id: int) -> CurriculumVersion | None:
    return (
        db.query(CurriculumVersion)
        .filter_by(program_id=program_id)
        .order_by(CurriculumVersion.id.desc())
        .first()
    )


def _course_blob(course: Course) -> str:
    parts = [course.name_tr or "", course.name_en or "", course.normalized_title or ""]
    if course.content:
        parts.extend(
            [
                course.content.description or "",
                course.content.weekly_content or "",
            ]
        )
    parts.extend(o.outcome_text for o in course.outcomes)
    return " ".join(parts)
