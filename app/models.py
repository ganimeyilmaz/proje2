from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(100))
    official_url: Mapped[str | None] = mapped_column(String(1000))
    adapter_name: Mapped[str] = mapped_column(String(100), default="generic_html")
    notes: Mapped[str | None] = mapped_column(Text)

    programs = relationship("Program", back_populates="university", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree_level: Mapped[str] = mapped_column(String(50), default="lisans")
    language: Mapped[str] = mapped_column(String(10), default="tr")
    faculty: Mapped[str | None] = mapped_column(String(255))
    official_url: Mapped[str | None] = mapped_column(String(1000))
    bologna_url: Mapped[str | None] = mapped_column(String(1000))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    university = relationship("University", back_populates="programs")
    curricula = relationship("CurriculumVersion", back_populates="program", cascade="all, delete-orphan")


class CurriculumVersion(Base):
    __tablename__ = "curriculum_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    academic_year: Mapped[str | None] = mapped_column(String(50))
    version_name: Mapped[str | None] = mapped_column(String(100))
    total_ects: Mapped[float | None] = mapped_column(Float)
    source_url: Mapped[str | None] = mapped_column(String(1000))
    quality_score: Mapped[float | None] = mapped_column(Float)

    program = relationship("Program", back_populates="curricula")
    semesters = relationship("Semester", back_populates="curriculum", cascade="all, delete-orphan")


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    curriculum_version_id: Mapped[int] = mapped_column(ForeignKey("curriculum_versions.id"))
    semester_no: Mapped[int | None] = mapped_column(Integer)
    semester_name: Mapped[str | None] = mapped_column(String(100))

    curriculum = relationship("CurriculumVersion", back_populates="semesters")
    courses = relationship("Course", back_populates="semester", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint(
            "semester_id",
            "code",
            "name_tr",
            name="uq_course_identity",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id"))
    code: Mapped[str | None] = mapped_column(String(50))
    name_tr: Mapped[str | None] = mapped_column(String(500))
    name_en: Mapped[str | None] = mapped_column(String(500))
    normalized_title: Mapped[str | None] = mapped_column(String(500))
    course_type: Mapped[str | None] = mapped_column(String(20))
    local_credit: Mapped[float | None] = mapped_column(Float)
    ects: Mapped[float | None] = mapped_column(Float)
    theory_hour: Mapped[float | None] = mapped_column(Float)
    practice_hour: Mapped[float | None] = mapped_column(Float)
    lab_hour: Mapped[float | None] = mapped_column(Float)
    detail_url: Mapped[str | None] = mapped_column(String(1000))
    topic_area: Mapped[str | None] = mapped_column(String(50))
    topic_confidence: Mapped[float | None] = mapped_column(Float)

    semester = relationship("Semester", back_populates="courses")
    content = relationship("CourseContent", back_populates="course", uselist=False, cascade="all, delete-orphan")
    outcomes = relationship("CourseLearningOutcome", back_populates="course", cascade="all, delete-orphan")


class CourseContent(Base):
    __tablename__ = "course_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), unique=True)
    purpose: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    weekly_content: Mapped[str | None] = mapped_column(Text)
    prerequisites: Mapped[str | None] = mapped_column(Text)
    teaching_methods: Mapped[str | None] = mapped_column(Text)

    course = relationship("Course", back_populates="content")


class CourseLearningOutcome(Base):
    __tablename__ = "course_learning_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    outcome_no: Mapped[int | None] = mapped_column(Integer)
    outcome_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(10))
    bloom_level: Mapped[str | None] = mapped_column(String(30))
    quality_flags: Mapped[str | None] = mapped_column(Text)

    course = relationship("Course", back_populates="outcomes")


class ProgramOutcome(Base):
    __tablename__ = "program_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    outcome_no: Mapped[int | None] = mapped_column(Integer)
    outcome_text: Mapped[str] = mapped_column(Text, nullable=False)


class SourceSnapshot(Base):
    __tablename__ = "source_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    fetch_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status_code: Mapped[int | None] = mapped_column(Integer)
    content_hash: Mapped[str | None] = mapped_column(String(64))
    parser_name: Mapped[str | None] = mapped_column(String(100))
    robots_allowed: Mapped[bool | None] = mapped_column(Boolean)
    error_message: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(500))


class ValidationIssue(Base):
    __tablename__ = "validation_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    issue_code: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_a: Mapped[str | None] = mapped_column(String(100))
    entity_b: Mapped[str | None] = mapped_column(String(100))
    analysis_type: Mapped[str] = mapped_column(String(80))
    metric_name: Mapped[str] = mapped_column(String(80))
    metric_value: Mapped[float | None] = mapped_column(Float)
    detail: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BenchmarkArea(Base):
    __tablename__ = "benchmark_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    framework: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255))
    keywords: Mapped[str] = mapped_column(Text)


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="open")
    gold_label: Mapped[str | None] = mapped_column(String(100))
