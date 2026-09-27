from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParsedOutcome:
    outcome_no: int | None
    text: str
    language: str | None = None


@dataclass
class ParsedCourse:
    code: str | None = None
    name_tr: str | None = None
    name_en: str | None = None
    semester_raw: str | None = None
    course_type_raw: str | None = None
    ects_raw: str | None = None
    local_credit_raw: str | None = None
    theory_raw: str | None = None
    practice_raw: str | None = None
    lab_raw: str | None = None
    detail_url: str | None = None
    purpose: str | None = None
    description: str | None = None
    weekly_content: str | None = None
    prerequisites: str | None = None
    teaching_methods: str | None = None
    outcomes: list[ParsedOutcome] = field(default_factory=list)


@dataclass
class ParsedCurriculum:
    academic_year: str | None = None
    version_name: str | None = None
    total_ects_raw: str | None = None
    courses: list[ParsedCourse] = field(default_factory=list)
    parser_name: str = "generic"


class UniversityCatalogAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def can_parse(self, html: str, url: str) -> bool:
        ...

    @abstractmethod
    def parse_curriculum(self, html: str, url: str) -> ParsedCurriculum:
        ...
