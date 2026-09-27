from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.crawler.adapters.base import (
    ParsedCourse,
    ParsedCurriculum,
    ParsedOutcome,
    UniversityCatalogAdapter,
)
from app.normalize.rules import fold_tr


HEADER_MAP = {
    "kod": "code",
    "code": "code",
    "ders kodu": "code",
    "ders adı": "name_tr",
    "ders adi": "name_tr",
    "dersin adı": "name_tr",    # <-- Erciyes için eklendi
    "dersin adi": "name_tr",    # <-- Erciyes için eklendi
    "course name": "name_en",
    "adı": "name_tr",
    "name": "name_en",
    "akts": "ects_raw",
    "ects": "ects_raw",
    "kredi": "local_credit_raw",
    "ulusal kredi": "local_credit_raw", # <-- Erciyes için eklendi (UK sütunu)
    "credit": "local_credit_raw",
    "türü": "course_type_raw",
    "turu": "course_type_raw",
    "type": "course_type_raw",
    "dönem": "semester_raw",
    "donem": "semester_raw",
    "yarıyıl": "semester_raw",
    "yariyil": "semester_raw",
    "semester": "semester_raw",
    "t": "theory_raw",
    "u": "practice_raw",
    "l": "lab_raw",
}


class GenericHtmlTableAdapter(UniversityCatalogAdapter):
    """HTML tablosundan ders listesi çıkaran genel adaptör."""

    name = "generic_html"

    def can_parse(self, html: str, url: str) -> bool:
        soup = BeautifulSoup(html, "lxml")
        return bool(soup.find("table"))

    def parse_curriculum(self, html: str, url: str) -> ParsedCurriculum:
        soup = BeautifulSoup(html, "lxml")
        courses: list[ParsedCourse] = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            headers = [self._cell_text(c).lower() for c in rows[0].find_all(["th", "td"])]
            # BURAYA PRINT EKLE VE TERMINALE BAK:
            print("TABLO BAŞLIKLARI:", headers)
            mapped = [HEADER_MAP.get(h) for h in headers]
            if not any(mapped):
                continue
            current_semester = None
            for row in rows[1:]:
                cells = [self._cell_text(c) for c in row.find_all(["td", "th"])]
                if len(cells) == 1 and cells[0]:
                    current_semester = cells[0]
                    continue
                if len(cells) < 2:
                    continue
                course = ParsedCourse()
                for idx, field in enumerate(mapped):
                    if field and idx < len(cells):
                        setattr(course, field, cells[idx] or None)
                if current_semester and not course.semester_raw:
                    course.semester_raw = current_semester
                link = row.find("a", href=True)
                if link:
                    course.detail_url = urljoin(url, link["href"])
                if course.name_tr or course.name_en or course.code:
                    courses.append(course)
        attach_outcomes_by_heading(soup, courses)
        return ParsedCurriculum(courses=courses, parser_name=self.name)

    @staticmethod
    def _cell_text(cell) -> str:
        return " ".join(cell.get_text(" ", strip=True).split())


def attach_outcomes_by_heading(soup: BeautifulSoup, courses: list[ParsedCourse]) -> None:
    if not courses:
        return
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        title = heading.get_text(" ", strip=True)
        folded_h = fold_tr(title)
        ul = heading.find_next("ol") or heading.find_next("ul")
        if not ul:
            continue
        items = [
            ParsedOutcome(outcome_no=i, text=li.get_text(" ", strip=True))
            for i, li in enumerate(ul.find_all("li"), start=1)
            if li.get_text(" ", strip=True)
        ]
        if not items:
            continue
        best = None
        best_score = 0
        for course in courses:
            name = fold_tr(course.name_tr or course.name_en or "")
            if not name:
                continue
            score = len(set(name.split()) & set(folded_h.split()))
            if name and name in folded_h:
                score += 3
            if score > best_score:
                best, best_score = course, score
        if best and best_score >= 2 and not best.outcomes:
            best.outcomes = items
