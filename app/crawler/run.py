from __future__ import annotations

from sqlalchemy.orm import Session

from app.analysis.pipeline import annotate_courses
from app.crawler.adapters import select_adapter
from app.crawler.http_client import FetchResult, HttpCrawler
from app.crawler.ingest import ingest_curriculum, persist_fetch
from app.models import Program, SourceSnapshot


def crawl_program(db: Session, program: Program, crawler: HttpCrawler | None = None) -> dict:
    url = program.bologna_url or program.official_url
    own_client = crawler is None
    crawler = crawler or HttpCrawler()
    try:
        if not url:
            persist_fetch(
                db,
                FetchResult(
                    url="",
                    status_code=None,
                    content=None,
                    content_hash=None,
                    title=None,
                    robots_allowed=None,
                    error_message="Program URL tanımlı değil",
                    fetched_at=__import__("datetime").datetime.utcnow(),
                ),
                "program",
                program.id,
                None,
            )
            db.commit()
            return {"ok": False, "reason": "no_url"}
        result = crawler.fetch(url)
        persist_fetch(db, result, "program", program.id, None)
        if not result.content or result.status_code != 200:
            db.commit()
            return {"ok": False, "reason": result.error_message or "fetch_failed"}
        html = result.content.decode("utf-8", errors="ignore")
        adapter = select_adapter(html, result.url, program.university.adapter_name)
        persist_fetch(db, result, "program", program.id, adapter.name)
        parsed = adapter.parse_curriculum(html, result.url)
        curriculum = ingest_curriculum(db, program, parsed, result.url)
        annotate_courses(db, curriculum)
        return {
            "ok": True,
            "curriculum_id": curriculum.id,
            "courses": sum(len(s.courses) for s in curriculum.semesters),
            "parser": adapter.name,
            "quality": curriculum.quality_score,
        }
    finally:
        if own_client:
            crawler.close()


def recent_failures(db: Session, limit: int = 50) -> list[SourceSnapshot]:
    return (
        db.query(SourceSnapshot)
        .filter(SourceSnapshot.error_message.isnot(None))
        .order_by(SourceSnapshot.id.desc())
        .limit(limit)
        .all()
    )
