from pathlib import Path

from app.crawler.adapters import select_adapter
from app.crawler.adapters.bologna import BolognaLikeAdapter
from app.crawler.adapters.generic_html import GenericHtmlTableAdapter
from app.normalize.rules import normalize_course_type, normalize_semester, normalize_title, parse_ects
from app.analysis.bloom import classify_bloom
from app.analysis.similarity import token_jaccard
from app.analysis.benchmark import classify_course


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_ects():
    assert parse_ects("5 AKTS") == 5.0
    assert parse_ects("5,5") == 5.5
    assert parse_ects("-") is None
    assert parse_ects("99") is None


def test_course_type_and_semester():
    assert normalize_course_type("Zorunlu") == "REQUIRED"
    assert normalize_course_type("Elective") == "ELECTIVE"
    assert normalize_semester("1. Yarıyıl") == 1
    assert normalize_semester("Semester 3") == 3


def test_normalize_title_variants():
    a = normalize_title("Veri Tabanı Sistemleri")
    b = normalize_title("Veritabanı Sistemleri")
    c = normalize_title("Database Systems")
    assert a == b
    assert "veri" in a or "veritabani" in a or a is not None
    assert c


def test_generic_adapter_fixture():
    html = (FIXTURES / "uni_a.html").read_text(encoding="utf-8")
    parsed = GenericHtmlTableAdapter().parse_curriculum(html, "https://a.example/plan")
    assert len(parsed.courses) == 10
    assert parsed.courses[0].code == "CENG101"
    assert parsed.courses[0].ects_raw == "6"


def test_bologna_adapter_and_selection():
    html = (FIXTURES / "uni_b.html").read_text(encoding="utf-8")
    adapter = select_adapter(html, "https://b.example/bologna")
    assert adapter.name == "bologna_like"
    parsed = BolognaLikeAdapter().parse_curriculum(html, "https://b.example/bologna")
    assert parsed.academic_year
    assert len(parsed.courses) >= 9


def test_bloom_and_topic():
    assert classify_bloom("Algoritmaların karmaşıklığını analiz eder.") == "analiz"
    area, conf, _ = classify_course("İşletim Sistemleri", "process thread kernel", "", "CENG301")
    assert area == "OS"
    assert conf > 0


def test_jaccard():
    assert token_jaccard("veri yapilari algoritmalar", "veri yapilari") > 0.4
