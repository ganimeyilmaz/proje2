from __future__ import annotations

from collections import defaultdict

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.analysis.pipeline import compare_programs, courses_of
from app.config import ROOT, settings
from app.db import SessionLocal, get_db
from app.demo import load_full_catalog
from app.models import (
    Course,
    CourseLearningOutcome,
    CurriculumVersion,
    Program,
    Semester,
    SourceSnapshot,
    University,
    ValidationIssue,
)
from app.seed import seed_benchmarks, seed_inventory
from app import models  # noqa: F401
from app.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
templates = Jinja2Templates(directory=str(ROOT / "app" / "templates"))
static_dir = ROOT / "app" / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        seed_benchmarks(db)
        seed_inventory(db)
        course_count = db.query(Course).count()
        program_count = db.query(Program).count()
        if program_count and course_count < program_count * 20:
            load_full_catalog(db, replace=True)
    finally:
        db.close()


def _dashboard_stats(db: Session) -> dict:
    unis = db.query(University).count()
    programs = db.query(Program).count()
    curricula = db.query(CurriculumVersion).count()
    courses = db.query(Course).count()
    with_lo = (
        db.query(Course.id)
        .join(Course.outcomes)
        .distinct()
        .count()
    )
    failed = (
        db.query(SourceSnapshot)
        .filter(SourceSnapshot.error_message.isnot(None))
        .count()
    )
    return {
        "universities": unis,
        "programs": programs,
        "accessed": curricula,
        "failed": failed,
        "courses": courses,
        "lo_courses": with_lo,
    }


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    programs = (
        db.query(Program)
        .options(
            joinedload(Program.university),
            joinedload(Program.curricula).joinedload(CurriculumVersion.semesters).joinedload(Semester.courses),
        )
        .all()
    )
    rows = []
    area_totals: dict[str, int] = defaultdict(int)
    for p in programs:
        cur = max(p.curricula, key=lambda c: c.id) if p.curricula else None
        courses = courses_of(cur, db) if cur else []
        for c in courses:
            if c.topic_area:
                area_totals[c.topic_area] += 1
        rows.append(
            {
                "program": p,
                "curriculum": cur,
                "quality": cur.quality_score if cur else None,
                "course_count": len(courses),
                "lo_count": sum(len(c.outcomes) for c in courses),
            }
        )
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "stats": _dashboard_stats(db),
            "rows": rows,
            "area_totals": dict(sorted(area_totals.items(), key=lambda x: -x[1])),
        },
    )


@app.get("/programs/{program_id}", response_class=HTMLResponse)
def program_card(program_id: int, request: Request, db: Session = Depends(get_db)):
    program = db.get(Program, program_id)
    curriculum = (
        db.query(CurriculumVersion)
        .options(
            joinedload(CurriculumVersion.semesters)
            .joinedload(Semester.courses)
            .joinedload(Course.outcomes),
            joinedload(CurriculumVersion.semesters)
            .joinedload(Semester.courses)
            .joinedload(Course.content),
        )
        .filter_by(program_id=program_id)
        .order_by(CurriculumVersion.id.desc())
        .first()
    )
    issues = []
    courses = []
    area_counts: dict[str, int] = defaultdict(int)
    bloom_counts: dict[str, int] = defaultdict(int)
    if curriculum:
        issues = (
            db.query(ValidationIssue)
            .filter_by(entity_type="curriculum", entity_id=curriculum.id)
            .all()
        )
        courses = courses_of(curriculum, db)
        courses.sort(key=lambda c: ((c.semester.semester_no or 99), c.code or ""))
        for c in courses:
            if c.topic_area:
                area_counts[c.topic_area] += 1
            for o in c.outcomes:
                if o.bloom_level:
                    bloom_counts[o.bloom_level] += 1
    return templates.TemplateResponse(
        "program.html",
        {
            "request": request,
            "program": program,
            "curriculum": curriculum,
            "issues": issues,
            "courses": courses,
            "area_counts": dict(area_counts),
            "bloom_counts": dict(bloom_counts),
        },
    )


@app.get("/compare", response_class=HTMLResponse)
def compare_form(request: Request, db: Session = Depends(get_db), a: int | None = None, b: int | None = None):
    programs = db.query(Program).options(joinedload(Program.university)).all()
    result = None
    if a and b:
        result = compare_programs(db, a, b)
    return templates.TemplateResponse(
        "compare.html",
        {"request": request, "programs": programs, "result": result, "a": a, "b": b},
    )


@app.get("/issues", response_class=HTMLResponse)
def issues(request: Request, db: Session = Depends(get_db)):
    snaps = (
        db.query(SourceSnapshot)
        .order_by(SourceSnapshot.id.desc())
        .limit(100)
        .all()
    )
    return templates.TemplateResponse("issues.html", {"request": request, "snaps": snaps})


@app.get("/export.csv")
def export_csv(db: Session = Depends(get_db)):
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["University", "Program", "Course", "ECTS", "LO Count", "Data Quality", "CS/SE Area"]
    )
    programs = db.query(Program).options(joinedload(Program.university), joinedload(Program.curricula)).all()
    for p in programs:
        cur = p.curricula[-1] if p.curricula else None
        if not cur:
            continue
        for s in cur.semesters:
            for c in s.courses:
                writer.writerow(
                    [
                        p.university.name,
                        p.name,
                        c.name_tr or c.name_en,
                        c.ects,
                        len(c.outcomes),
                        cur.quality_score,
                        c.topic_area,
                    ]
                )
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mufredat.csv"},
    )


@app.post("/programs/{program_id}/crawl")
def crawl_one(program_id: int, db: Session = Depends(get_db)):
    from fastapi.responses import RedirectResponse
    from app.crawler.run import crawl_program

    program = db.get(Program, program_id)
    if program:
        crawl_program(db, program)
    return RedirectResponse(url=f"/programs/{program_id}", status_code=303)


@app.post("/programs")
def add_program(
    university_name: str = Form(...),
    program_name: str = Form(...),
    bologna_url: str = Form(""),
    db: Session = Depends(get_db),
):
    from fastapi.responses import RedirectResponse

    uni = db.query(University).filter_by(name=university_name).one_or_none()
    if not uni:
        uni = University(name=university_name, adapter_name="generic_html")
        db.add(uni)
        db.flush()
    db.add(
        Program(
            university_id=uni.id,
            name=program_name,
            bologna_url=bologna_url or None,
            official_url=bologna_url or None,
        )
    )
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/reload-demo")
def reload_demo(db: Session = Depends(get_db)):
    from fastapi.responses import RedirectResponse

    load_full_catalog(db, replace=True)
    return RedirectResponse(url="/", status_code=303)
