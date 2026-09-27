from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from app.analysis.benchmark import CS2023, SEEK
from app.models import BenchmarkArea, Program, University

SEED_CSV = Path(__file__).resolve().parent.parent / "seed" / "universities.csv"


def seed_benchmarks(db: Session) -> None:
    if db.query(BenchmarkArea).count():
        return
    for code, (name, kws) in CS2023.items():
        db.add(BenchmarkArea(framework="CS2023", code=code, name=name, keywords=kws))
    for code, (name, kws) in SEEK.items():
        db.add(BenchmarkArea(framework="SE2014", code=code, name=name, keywords=kws))
    db.commit()


def seed_inventory(db: Session) -> None:
    if not SEED_CSV.exists():
        return
    with SEED_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uni = (
                db.query(University)
                .filter_by(name=row["university_name"])
                .one_or_none()
            )
            if not uni:
                uni = University(
                    name=row["university_name"],
                    type=row.get("university_type") or None,
                    city=row.get("city") or None,
                    official_url=row.get("official_url") or None,
                    adapter_name=row.get("adapter") or "generic_html",
                )
                db.add(uni)
                db.flush()
            exists = (
                db.query(Program)
                .filter_by(university_id=uni.id, name=row["program_name"], language=row.get("language") or "tr")
                .one_or_none()
            )
            if exists:
                continue
            db.add(
                Program(
                    university_id=uni.id,
                    name=row["program_name"],
                    degree_level="lisans",
                    language=row.get("language") or "tr",
                    faculty=row.get("faculty") or None,
                    official_url=row.get("program_url") or None,
                    bologna_url=row.get("bologna_url") or None,
                )
            )
    db.commit()
