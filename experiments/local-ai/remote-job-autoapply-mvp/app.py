from datetime import date
from pathlib import Path
from typing import Callable

from config import (
    CANDIDATE_PROFILE_PATH,
    MASTER_RESUME_PATH,
    MIN_RELEVANCE_SCORE,
    MAX_APPLICATIONS_PER_DAY,
    OPENAI_API_KEY,
)
from db import init_db, get_session, Job, Application
from scrapers.remoteok import fetch_remoteok_jobs
from scrapers.weworkremotely import fetch_weworkremotely_jobs
from scrapers.linkedin import fetch_linkedin_jobs
from scrapers.company_pages import fetch_company_careers_jobs
from ai.scorer import score_job_relevance
from ai.resume_tailor import tailor_resume
from ai.cover_letter import generate_cover_letter
from automator.apply_playwright import submit_application


def load_text(path: Path, fallback: str) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else fallback


def _safe_fetch(fetcher: Callable[..., list], *args) -> list:
    try:
        return fetcher(*args)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Source failed: {fetcher.__name__}: {exc}")
        return []


def upsert_jobs() -> None:
    session = get_session()
    all_jobs = (
        _safe_fetch(fetch_remoteok_jobs, 10)
        + _safe_fetch(fetch_weworkremotely_jobs, 10)
        + _safe_fetch(fetch_linkedin_jobs, 10)
        + _safe_fetch(fetch_company_careers_jobs, ["https://boards.greenhouse.io"], 3)
    )

    for j in all_jobs:
        exists = session.query(Job).filter_by(application_link=str(j.application_link)).first()
        if exists:
            continue
        session.add(
            Job(
                source=j.source,
                company=j.company,
                title=j.title,
                description=j.description,
                location=j.location,
                application_link=str(j.application_link),
            )
        )
    session.commit()
    session.close()
    print(f"[INFO] Stored/updated jobs from sources: {len(all_jobs)} candidates collected.")


def apply_pipeline(dry_run: bool = True) -> None:
    if not OPENAI_API_KEY:
        print("[WARN] OPENAI_API_KEY is missing. Skipping AI scoring + auto-apply stage.")
        return

    profile = load_text(CANDIDATE_PROFILE_PATH, "Python backend engineer with cloud/devops experience")
    master_resume = load_text(MASTER_RESUME_PATH, "Master resume placeholder")

    session = get_session()
    applied_today = session.query(Application).filter(Application.date_applied >= date.today()).count()
    remaining = max(0, MAX_APPLICATIONS_PER_DAY - applied_today)

    jobs = (
        session.query(Job)
        .filter(Job.relevance_score.is_(None))
        .order_by(Job.date_found.desc())
        .limit(50)
        .all()
    )

    for job in jobs:
        score = score_job_relevance(profile, job.description)
        job.relevance_score = score
    session.commit()

    targets = (
        session.query(Job)
        .filter(Job.relevance_score >= MIN_RELEVANCE_SCORE)
        .limit(remaining)
        .all()
    )

    for job in targets:
        existing = session.query(Application).filter_by(job_id=job.id).first()
        if existing:
            continue

        resume_path = Path(f"data/resume_job_{job.id}.txt")
        cover_path = Path(f"data/cover_job_{job.id}.txt")
        tailor_resume(master_resume, job.description, resume_path)
        generate_cover_letter(job.company, job.title, profile, cover_path)

        submit_application(
            application_url=job.application_link,
            full_name="YOUR NAME",
            email="your@email.com",
            resume_path=resume_path,
            cover_letter_path=cover_path,
            dry_run=dry_run,
        )

        session.add(
            Application(
                job_id=job.id,
                status="applied",
                tailored_resume_path=str(resume_path),
                cover_letter_path=str(cover_path),
            )
        )
        session.commit()

    session.close()


if __name__ == "__main__":
    init_db()
    upsert_jobs()
    apply_pipeline(dry_run=True)
    print("Pipeline completed. Set dry_run=False after validating selectors and platform compliance.")
