from __future__ import annotations

import re

from bs4 import BeautifulSoup

from app.crawler.adapters.base import (
    ParsedCourse,
    ParsedCurriculum,
    ParsedOutcome,
    UniversityCatalogAdapter,
)
from app.crawler.adapters.generic_html import GenericHtmlTableAdapter, attach_outcomes_by_heading


class BolognaLikeAdapter(UniversityCatalogAdapter):
    """OBS/Bologna tarzı ders bilgi paketi sayfaları için ikinci adaptör."""

    name = "bologna_like"

    def can_parse(self, html: str, url: str) -> bool:
        haystack = (html + url).lower()
        return any(
            token in haystack
            for token in ("bologna", "akts", "ects", "ders bilgi", "öğrenme çıkt", "ogrenme cikt")
        )

    def parse_curriculum(self, html: str, url: str) -> ParsedCurriculum:
        generic = GenericHtmlTableAdapter().parse_curriculum(html, url)
        soup = BeautifulSoup(html, "lxml")
        year = None
        blob = soup.get_text(" ", strip=True)
        match = re.search(r"(20\d{2}\s*/\s*20\d{2}|20\d{2})", blob)
        if match:
            year = match.group(1)
        generic.academic_year = year
        generic.parser_name = self.name
        if not generic.courses:
            generic.courses = self._parse_definition_lists(soup)
        self._attach_inline_outcomes(soup, generic.courses)
        attach_outcomes_by_heading(soup, generic.courses)
        return generic

    def _parse_definition_lists(self, soup: BeautifulSoup) -> list[ParsedCourse]:
        courses: list[ParsedCourse] = []
        for block in soup.select(".course, .ders, article, .panel"):
            title = block.find(["h2", "h3", "h4", "strong"])
            if not title:
                continue
            course = ParsedCourse(name_tr=title.get_text(" ", strip=True))
            text = block.get_text("\n", strip=True)
            code = re.search(r"\b([A-Z]{2,5}\s?\d{3,4})\b", text)
            if code:
                course.code = code.group(1)
            ects = re.search(r"AKTS\s*[:\-]?\s*(\d+(?:[.,]\d+)?)", text, re.I)
            if ects:
                course.ects_raw = ects.group(1)
            outcomes = []
            for idx, li in enumerate(block.select("li"), start=1):
                t = li.get_text(" ", strip=True)
                if t:
                    outcomes.append(ParsedOutcome(outcome_no=idx, text=t))
            course.outcomes = outcomes
            courses.append(course)
        return courses

    def _attach_inline_outcomes(self, soup: BeautifulSoup, courses: list[ParsedCourse]) -> None:
        headings = soup.find_all(string=re.compile(r"öğrenme çıkt|learning outcome", re.I))
        if not headings or not courses:
            return
        items = []
        for heading in headings:
            parent = heading.parent
            if not parent:
                continue
            ul = parent.find_next("ol") or parent.find_next("ul")
            if ul:
                for idx, li in enumerate(ul.find_all("li"), start=1):
                    items.append(ParsedOutcome(outcome_no=idx, text=li.get_text(" ", strip=True)))
        if len(courses) == 1 and items and not courses[0].outcomes:
            courses[0].outcomes = items
