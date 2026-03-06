# Remote Job Auto-Apply MVP (Python)

A **minimal but functional local automation system** to discover remote jobs, filter with AI, generate tailored materials, and submit applications with safe limits.

> Compliance-first defaults: no login scraping required, dry-run submission enabled, and daily application cap.

## 1) System architecture diagram

```mermaid
flowchart TD
    A[Job Sources\nLinkedIn guest jobs\nRemoteOK API\nWeWorkRemotely\nCompany career pages] --> B[Scraper Layer]
    B --> C[(SQLite DB: jobs)]
    C --> D[AI Relevance Scorer\n1-10 score]
    D --> E{Score >= threshold?}
    E -- No --> C
    E -- Yes --> F[Resume Tailoring Module]
    E -- Yes --> G[Cover Letter Generator]
    F --> H[(Generated resume files)]
    G --> I[(Generated cover letters)]
    H --> J[Playwright Application Bot\n(dry-run by default)]
    I --> J
    J --> K[(SQLite DB: applications)]
    K --> L[Streamlit Dashboard]
```

## 2) Folder structure

```text
remote-job-autoapply-mvp/
├── .env.example
├── requirements.txt
├── app.py
├── config.py
├── db.py
├── models.py
├── dashboard.py
├── data/
│   ├── candidate_profile.txt
│   └── master_resume.txt
├── ai/
│   ├── client.py
│   ├── scorer.py
│   ├── resume_tailor.py
│   └── cover_letter.py
├── scrapers/
│   ├── linkedin.py
│   ├── remoteok.py
│   ├── weworkremotely.py
│   └── company_pages.py
└── automator/
    └── apply_playwright.py
```

## 3) Recommended libraries

- `requests` + `beautifulsoup4` for ingestion
- `SQLAlchemy` + `SQLite` for persistence
- `openai` for relevance scoring + text generation only
- `playwright` for browser automation
- `streamlit` + `pandas` for local tracking dashboard
- `python-dotenv` for local config

## 4) Minimal working modules

- **Scraping jobs:** `scrapers/*`
- **Saving jobs/applications:** `db.py`
- **AI filter (1-10):** `ai/scorer.py`
- **Tailored resume generation:** `ai/resume_tailor.py`
- **Cover letter generation:** `ai/cover_letter.py`
- **Submission automation:** `automator/apply_playwright.py`
- **Orchestration pipeline:** `app.py`
- **Tracker dashboard:** `dashboard.py`

## 5) Run locally

### Step 1 — Setup

```bash
cd experiments/local-ai/remote-job-autoapply-mvp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

### Step 2 — Add personal inputs

Create files:

- `data/candidate_profile.txt`
- `data/master_resume.txt`

### Step 3 — Run pipeline

```bash
python app.py
```

This will:

1. scrape jobs,
2. store in SQLite,
3. score fit with AI,
4. generate tailored resume + cover letter,
5. attempt **dry-run** form filling,
6. track applications.

### Step 4 — View dashboard

```bash
streamlit run dashboard.py
```


## Troubleshooting

- **WeWorkRemotely 403 Forbidden**: some environments are blocked. The scraper now fails open (returns no jobs) so the pipeline continues with LinkedIn/RemoteOK/company pages.
- If a source blocks requests, keep the source enabled but treat it as optional; the orchestrator will continue collecting from remaining providers.

## 6) Safe-by-default compliance controls

- Uses public job pages/endpoints where possible.
- Defaults to `dry_run=True` for submission bot.
- Caps applications/day via `MAX_APPLICATIONS_PER_DAY`.
- Encourages manual selector checks per platform ATS form.
- Avoids brute force / high-frequency behavior.

## 7) SaaS scaling ideas

1. Multi-tenant PostgreSQL + row-level security.
2. Queue workers (Celery/RQ) for scrape/score/apply pipelines.
3. Provider abstraction for multiple LLM backends.
4. Human approval inbox before submit.
5. ATS adapters (Greenhouse, Lever, Workday) with site-specific selectors.
6. Team analytics: conversion rate by source/role/company.
7. Billing + usage caps + audit logging.
8. Browser session vault for secure credential handling.

## Notes

- LinkedIn/ATS policies evolve; validate terms before enabling real submissions.
- Keep manual review in loop for high-quality, non-spam applications.
