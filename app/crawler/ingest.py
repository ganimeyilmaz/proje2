from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.crawler.adapters.base import ParsedCourse, ParsedCurriculum
from app.models import (
    Course,
    CourseContent,
    CourseLearningOutcome,
    CurriculumVersion,
    Program,
    Semester,
    SourceSnapshot,
    ValidationIssue,
)
from app.normalize.rules import (
    empty_to_none,
    normalize_course_type,
    normalize_semester,
    normalize_title,
    parse_ects,
)
from app.quality.engine import QUALITY_WEIGHTS, evaluate_curriculum


def persist_fetch(db: Session, result, entity_type: str, entity_id: int | None, parser: str | None):
    snap = SourceSnapshot(
        entity_type=entity_type,
        entity_id=entity_id,
        url=result.url,
        fetch_date=result.fetched_at,
        status_code=result.status_code,
        content_hash=result.content_hash,
        parser_name=parser,
        robots_allowed=result.robots_allowed,
        error_message=result.error_message,
        title=result.title,
    )
    db.add(snap)
    db.flush()
    return snap


def ingest_curriculum(
    db: Session,
    program: Program,
    parsed: ParsedCurriculum,
    source_url: str,
) -> CurriculumVersion:
    existing = (
        db.query(CurriculumVersion)
        .filter_by(program_id=program.id, source_url=source_url)
        .one_or_none()
    )
    curriculum = existing or CurriculumVersion(program_id=program.id, source_url=source_url)
    curriculum.academic_year = parsed.academic_year
    curriculum.version_name = parsed.version_name
    curriculum.total_ects = parse_ects(parsed.total_ects_raw)
    db.add(curriculum)
    db.flush()

    db.query(ValidationIssue).filter_by(
        entity_type="curriculum", entity_id=curriculum.id
    ).delete()

    grouped: dict[int | None, list[ParsedCourse]] = defaultdict(list)
    for course in parsed.courses:
        grouped[normalize_semester(course.semester_raw)].append(course)

    # Replace semesters/courses for idempotency
    for sem in list(curriculum.semesters):
        db.delete(sem)
    db.flush()

    persisted: list[Course] = []
    for sem_no, courses in grouped.items():
        semester = Semester(
            curriculum_version_id=curriculum.id,
            semester_no=sem_no,
            semester_name=str(sem_no) if sem_no else "belirsiz",
        )
        db.add(semester)
        db.flush()
        for raw in courses:
            persisted.append(persist_course(db, semester, raw))

    issues, score = evaluate_curriculum(curriculum, persisted)
    curriculum.quality_score = score
    for issue in issues:
        db.add(
            ValidationIssue(
                entity_type="curriculum",
                entity_id=curriculum.id,
                issue_code=issue["code"],
                severity=issue["severity"],
                description=issue["description"],
            )
        )
    db.commit()
    db.refresh(curriculum)
    return curriculum


def persist_course(db: Session, semester: Semester, raw: ParsedCourse) -> Course:
    course = Course(
        semester_id=semester.id,
        code=empty_to_none(raw.code),
        name_tr=empty_to_none(raw.name_tr),
        name_en=empty_to_none(raw.name_en),
        normalized_title=normalize_title(raw.name_tr or raw.name_en),
        course_type=normalize_course_type(raw.course_type_raw),
        local_credit=parse_ects(raw.local_credit_raw),
        ects=parse_ects(raw.ects_raw),
        theory_hour=parse_ects(raw.theory_raw),
        practice_hour=parse_ects(raw.practice_raw),
        lab_hour=parse_ects(raw.lab_raw),
        detail_url=empty_to_none(raw.detail_url),
    )
    db.add(course)
    db.flush()
    if any([raw.purpose, raw.description, raw.weekly_content, raw.prerequisites, raw.teaching_methods]):
        course.content = CourseContent(
            course_id=course.id,
            purpose=raw.purpose,
            description=raw.description,
            weekly_content=raw.weekly_content,
            prerequisites=raw.prerequisites,
            teaching_methods=raw.teaching_methods,
        )
    for outcome in raw.outcomes:
        text = empty_to_none(outcome.text)
        if not text:
            continue
        course.outcomes.append(
            CourseLearningOutcome(
                course_id=course.id,
                outcome_no=outcome.outcome_no,
                outcome_text=text,
                language=outcome.language,
            )
        )
    return course


def quality_weights() -> dict[str, int]:
    return dict(QUALITY_WEIGHTS)
