from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.analysis.pipeline import annotate_courses
from app.catalog import curriculum_for_program
from app.crawler.http_client import FetchResult
from app.crawler.ingest import ingest_curriculum, persist_fetch
from app.models import Program, ValidationIssue


def load_full_catalog(db: Session, replace: bool = True) -> int:
    """Her program için 8 dönemlik dolu müfredat basar."""
    programs = (
        db.query(Program)
        .options(joinedload(Program.university), joinedload(Program.curricula))
        .all()
    )
    loaded = 0
    for program in programs:
        if replace:
            for cur in list(program.curricula):
                db.query(ValidationIssue).filter_by(
                    entity_type="curriculum", entity_id=cur.id
                ).delete()
                db.delete(cur)
            db.flush()
        elif program.curricula:
            continue
        parsed = curriculum_for_program(program)
        url = f"file://katalog/{program.university.name}/{program.name}"
        result = FetchResult(
            url=url,
            status_code=200,
            content=b"catalog-seed",
            content_hash="catalog",
            title=f"{program.university.name} katalog",
            robots_allowed=True,
            error_message=None,
            fetched_at=datetime.utcnow(),
        )
        persist_fetch(db, result, "program", program.id, "catalog_seed")
        curriculum = ingest_curriculum(db, program, parsed, url)
        annotate_courses(db, curriculum)
        loaded += 1
    return loaded
