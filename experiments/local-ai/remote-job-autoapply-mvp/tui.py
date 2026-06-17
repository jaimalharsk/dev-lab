#!/usr/bin/env python3
"""Terminal dashboard for the remote job auto-apply pipeline.

--demo replays the sample dataset (data/sample_jobs.json) with timed
reveals — no API key needed, deterministic pacing, built for screen
recordings and demo videos.

Without --demo, it shows the live pipeline state from the SQLite
database that app.py populates.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ai.schemas import CoverLetter, JobRelevanceResult, LivenessResult, SalaryRange, TailoredResume
from config import MIN_RELEVANCE_SCORE, MIN_SALARY

console = Console()

FIT_STYLE = {"high": "bold green", "medium": "bold yellow", "low": "bold red"}
LIVENESS_STYLE = {"active": "green", "expired": "red", "uncertain": "yellow"}
STEP_DELAY = 1.7


def load_demo_dataset() -> list[dict]:
    path = Path(__file__).resolve().parent / "data" / "sample_jobs.json"
    return json.loads(path.read_text(encoding="utf-8"))


def score_bar(label: str, value: float, width: int = 18) -> Text:
    filled = round(value * width)
    color = "green" if value >= 0.75 else "yellow" if value >= 0.5 else "red"
    text = Text()
    text.append(f"{label:<17}", style="dim")
    text.append("█" * filled, style=color)
    text.append("░" * (width - filled), style="grey23")
    text.append(f"  {value:.2f}", style="bold")
    return text


def build_header() -> Panel:
    return Panel(
        Text(
            "REMOTE JOB AUTO-APPLY — PIPELINE MONITOR   ·   structured-output demo replay",
            justify="center",
            style="bold white on dark_blue",
        ),
        border_style="blue",
    )


def build_table(jobs: list[dict], current: int) -> Table:
    table = Table(expand=True, border_style="grey50", header_style="bold white")
    table.add_column("Company", style="bold cyan", no_wrap=True)
    table.add_column("Role")
    table.add_column("Liveness", justify="center")
    table.add_column("Salary", justify="right")
    table.add_column("Score", justify="center")
    table.add_column("Fit", justify="center")
    table.add_column("Outcome")

    for i, job in enumerate(jobs):
        if i > current:
            table.add_row(job["company"], job["title"], "[dim]…[/dim]", "[dim]—[/dim]", "[dim]—[/dim]", "[dim]—[/dim]", "[dim]queued[/dim]")
            continue

        liveness = job.get("liveness_check")
        scoring = job.get("ai_scoring")
        salary_data = job.get("salary_range")

        liveness_cell = f"[{LIVENESS_STYLE.get(liveness['status'], 'white')}]{liveness['status']}[/]" if liveness else "—"

        salary_cell = "—"
        if salary_data and liveness and liveness.get("status") != "expired":
            sal = SalaryRange.model_validate(salary_data)
            salary_cell = f"[dim]{sal.display()}[/dim]"

        score_cell = f"{scoring['score']}/10" if scoring else "—"
        fit_cell = f"[{FIT_STYLE.get(scoring['fit_level'], 'white')}]{scoring['fit_level']}[/]" if scoring else "—"

        if i == current:
            outcome = "[bold cyan]▸ processing…[/bold cyan]"
        elif liveness and liveness["status"] == "expired":
            outcome = "[red]dropped — no AI tokens spent[/red]"
        elif scoring and scoring["score"] >= MIN_RELEVANCE_SCORE:
            outcome = "[green]✓ resume + cover letter generated[/green]"
        elif scoring:
            outcome = "[yellow]below threshold — skipped[/yellow]"
        else:
            outcome = ""

        table.add_row(job["company"], job["title"], liveness_cell, salary_cell, score_cell, fit_cell, outcome)

    return table


def build_detail(job: dict, stage: str) -> Panel:
    items: list = [Text(f"{job['company']} — {job['title']}", style="bold underline"), Text("")]

    if stage == "liveness":
        items.append(Text("Checking posting liveness before spending any AI tokens…", style="italic dim"))

    elif stage == "expired":
        liveness = LivenessResult.model_validate(job["liveness_check"])
        items.append(Text(f"status:  {liveness.status}", style="bold red"))
        items.append(Text(f"reason:  {liveness.reason}", style="dim"))
        items.append(Text(""))
        items.append(Text("→ LivenessResult validated. Job removed from DB.", style="italic"))
        items.append(Text("  Scorer was never called — zero tokens spent on a dead listing.", style="italic dim"))

    elif stage == "salary":
        salary = SalaryRange.model_validate(job["salary_range"])
        items.append(Text("SalaryRange", style="bold"))
        items.append(Text(f"  is_disclosed:  {salary.is_disclosed}", style="dim"))
        items.append(Text(f"  range:         {salary.display()}", style="bold green" if salary.is_disclosed else "yellow"))
        items.append(Text(f"  currency:      {salary.currency}   period: {salary.period}", style="dim"))
        items.append(Text(""))
        floor_note = f"≥ ${MIN_SALARY:,}/yr  ✓" if MIN_SALARY > 0 else "no floor configured"
        items.append(Text(f"  floor check:   {floor_note}", style="dim"))
        items.append(Text(""))
        items.append(Text("→ SalaryRange validated. Proceeding to score.", style="italic"))

    elif stage == "scoring":
        liveness = LivenessResult.model_validate(job["liveness_check"])
        items.append(Text(f"liveness:  {liveness.status}  ({liveness.reason})", style="dim"))
        items.append(Text(""))
        items.append(Text("Scoring across four weighted dimensions…", style="italic dim"))

    elif stage == "scored":
        result = JobRelevanceResult.model_validate(job["ai_scoring"])
        items.append(Text("JobRelevanceResult", style="bold"))
        items.append(score_bar("role_match", result.role_match))
        items.append(score_bar("level_fit", result.level_fit))
        items.append(score_bar("growth_potential", result.growth_potential))
        items.append(score_bar("remote_alignment", result.remote_alignment))
        items.append(Text(""))
        items.append(Text(f"composite score → {result.score}/10   (fit: {result.fit_level})", style="bold"))
        items.append(Text(""))
        items.append(Text("reasons:", style="bold"))
        for reason in result.reasons:
            items.append(Text(f"  • {reason}", style="dim"))

    elif stage == "materials":
        result = JobRelevanceResult.model_validate(job["ai_scoring"])
        items.append(Text(f"score {result.score}/10 ≥ threshold {MIN_RELEVANCE_SCORE} — generating tailored materials…", style="italic"))
        items.append(Text(""))
        if "tailored_resume" in job:
            resume = TailoredResume.model_validate(job["tailored_resume"])
            items.append(Text("TailoredResume.summary", style="bold"))
            items.append(Text(f"  {resume.summary}", style="dim"))
            items.append(Text(""))
        if "cover_letter" in job:
            letter = CoverLetter.model_validate(job["cover_letter"])
            items.append(Text("CoverLetter (opening + body excerpt)", style="bold"))
            items.append(Text(f"  {letter.opening}", style="dim"))
            items.append(Text(f"  {letter.body[:170]}…", style="dim"))

    return Panel(Group(*items), title="[bold]Structured Output — live validation[/bold]", border_style="cyan")


def build_footer(processed: list[dict]) -> Panel:
    expired = sum(1 for j in processed if (j.get("liveness_check") or {}).get("status") == "expired")
    scored = sum(1 for j in processed if j.get("ai_scoring"))
    generated = sum(1 for j in processed if j.get("ai_scoring") and j["ai_scoring"]["score"] >= MIN_RELEVANCE_SCORE)

    text = Text(justify="center")
    text.append(f"  scanned {len(processed)}  ", style="bold")
    text.append(f"│  dropped at liveness {expired}  ", style="red")
    text.append(f"│  scored {scored}  ", style="yellow")
    text.append(f"│  materials generated {generated}  ", style="green")
    return Panel(text, border_style="grey50")


def run_demo() -> None:
    jobs = load_demo_dataset()
    completed: list[dict] = []

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="table", size=len(jobs) + 5),
        Layout(name="detail"),
        Layout(name="footer", size=3),
    )
    layout["header"].update(build_header())
    layout["footer"].update(build_footer(completed))

    with Live(layout, console=console, refresh_per_second=8, screen=True):
        for i, job in enumerate(jobs):
            liveness = job.get("liveness_check")
            scoring = job.get("ai_scoring")

            layout["table"].update(build_table(jobs, i))
            layout["detail"].update(build_detail(job, "liveness"))
            time.sleep(STEP_DELAY)

            if liveness and liveness["status"] == "expired":
                layout["detail"].update(build_detail(job, "expired"))
                time.sleep(STEP_DELAY * 1.6)
                completed.append(job)
                layout["table"].update(build_table(jobs, i))
                layout["footer"].update(build_footer(completed))
                time.sleep(STEP_DELAY)
                continue

            layout["detail"].update(build_detail(job, "salary"))
            time.sleep(STEP_DELAY)

            layout["detail"].update(build_detail(job, "scoring"))
            time.sleep(STEP_DELAY)

            layout["detail"].update(build_detail(job, "scored"))
            layout["table"].update(build_table(jobs, i))
            time.sleep(STEP_DELAY * 1.6)

            if scoring and scoring["score"] >= MIN_RELEVANCE_SCORE:
                layout["detail"].update(build_detail(job, "materials"))
                time.sleep(STEP_DELAY * 1.8)

            completed.append(job)
            layout["footer"].update(build_footer(completed))
            time.sleep(STEP_DELAY)

        layout["detail"].update(
            Panel(
                Align.center(
                    Text(
                        "Pipeline complete.\n\n"
                        "Every value shown above passed Pydantic validation\n"
                        "before being written to disk or the database.",
                        style="bold green",
                        justify="center",
                    ),
                    vertical="middle",
                ),
                border_style="green",
            )
        )
        time.sleep(3.5)


def run_live() -> None:
    from db import Application, Job, get_session

    session = get_session()
    jobs = session.query(Job).order_by(Job.date_found.desc()).limit(20).all()
    if not jobs:
        console.print("[yellow]No jobs in the database yet. Run `python app.py` first, or use --demo.[/yellow]")
        session.close()
        return

    table = Table(title="Live Pipeline State", expand=True, border_style="grey50")
    table.add_column("Company", style="bold cyan")
    table.add_column("Role")
    table.add_column("Salary", justify="right")
    table.add_column("Score", justify="center")
    table.add_column("Applied", justify="center")
    table.add_column("Follow-up due", justify="center")
    table.add_column("Outcome", justify="center")

    OUTCOME_STYLE = {
        "pending": "dim",
        "no_response": "yellow",
        "interview": "bold cyan",
        "rejected": "red",
        "offer": "bold green",
    }

    for job in jobs:
        application = session.query(Application).filter_by(job_id=job.id).first()
        salary_cell = "—"
        if job.min_salary:
            sym = "$" if job.salary_currency in (None, "USD") else job.salary_currency
            hi = f"–{sym}{job.max_salary:,}" if job.max_salary else "+"
            salary_cell = f"{sym}{job.min_salary:,}{hi}"
        score_cell = f"{job.relevance_score}/10" if job.relevance_score is not None else "—"
        applied_cell = "[green]✓[/green]" if application else "[dim]—[/dim]"
        follow_up_cell = "—"
        outcome_cell = "—"
        if application:
            if application.follow_up_date:
                follow_up_cell = application.follow_up_date.strftime("%Y-%m-%d")
            style = OUTCOME_STYLE.get(application.outcome, "white")
            outcome_cell = f"[{style}]{application.outcome}[/]"
        table.add_row(job.company, job.title, salary_cell, score_cell, applied_cell, follow_up_cell, outcome_cell)

    console.print(table)
    session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Terminal dashboard for the job auto-apply pipeline")
    parser.add_argument("--demo", action="store_true", help="Replay the sample dataset with timed reveals (no API key needed)")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_live()


if __name__ == "__main__":
    main()
