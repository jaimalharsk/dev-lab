# Presentation Slides — Remote Job Auto-Apply Pipeline

---

## Slide 1 — Title & Problem

**Title:** Remote Job Auto-Apply Pipeline
**Subtitle:** A structured-output LLM workflow that filters, scores, and applies — automatically

**Body:**
- Applying to remote jobs is high-effort and mostly wasted: hours tailoring a resume for a listing that's already closed, or a role that's a bad fit
- Automating it with a plain LLM gives you unstructured text you can't safely use in a pipeline
- **This project solves both:** dead listings are filtered before any AI tokens are spent, and every AI output is a validated, typed Pydantic model

**Visual suggestion:** split diagram — left side shows the manual pain (crossed-out postings, wasted docs), right side shows the automated pipeline

---

## Slide 2 — Architecture & Pipeline Flow

**Title:** How the Pipeline Works

**Steps (left to right or top to bottom):**
1. **Scrape** — RemoteOK, WeWorkRemotely, LinkedIn, company career pages
2. **Liveness check** → `LivenessResult` — expired postings dropped immediately, zero tokens spent
3. **Salary extraction** → `SalaryRange` — discard below-floor roles before scoring
4. **Multi-dimensional scoring** → `JobRelevanceResult` — 4 sub-scores, composite computed in Python
5. **Material generation** → `TailoredResume` + `CoverLetter` — only for jobs above threshold
6. **Application bot** — Playwright form submission (dry-run by default)
7. **Follow-up tracker** — outcome recorded per application; summary printed each run

**Visual suggestion:** horizontal flowchart with colour-coded gates (red = drop, green = proceed)

---

## Slide 3 — Structured Output: The Core Idea

**Title:** Every AI Step Returns a Validated Model

**Key point:** The LLM never returns free text — it returns a typed Pydantic object. If the output doesn't fit the schema, the pipeline fails loudly instead of passing bad data downstream.

**Schema table:**

| Schema | Key Fields |
|--------|-----------|
| `LivenessResult` | `status` (active / expired / uncertain), `reason` |
| `SalaryRange` | `is_disclosed`, `min_salary`, `max_salary`, `currency`, `period` |
| `JobRelevanceResult` | `role_match`, `level_fit`, `growth_potential`, `remote_alignment` (0–1 each) + computed `score` |
| `CoverLetter` | `opening`, `body`, `closing` |
| `TailoredResume` | `summary`, `skills[]`, `experience[]`, `education[]` |

**Scoring formula:**
```
score = round((role_match × 0.45 + level_fit × 0.30
             + growth_potential × 0.15 + remote_alignment × 0.10) × 10)
```
The LLM scores the dimensions. The weights and arithmetic live in your code, not the prompt.

**Visual suggestion:** show a code snippet of `client.beta.chat.completions.parse(response_format=JobRelevanceResult)` alongside the Pydantic model definition

---

## Slide 4 — Token Efficiency & Design Decisions

**Title:** Smart Gates Save Tokens (and Time)

**Three-gate design — each gate only runs if the previous one passes:**

| Gate | Schema | What it prevents |
|------|--------|-----------------|
| Liveness | `LivenessResult` | Scoring a closed posting |
| Salary floor | `SalaryRange` | Scoring an underpaying role |
| Relevance threshold | `JobRelevanceResult` | Generating materials for a poor fit |

**Other design decisions:**

- **Composite score computed in Python** — not prompt-engineered. Weights are code, not magic words.
- **`dry_run=True` by default** — Playwright fills forms but never submits without explicit opt-in
- **Outcome tracking** — each application records `outcome` (pending → interview / rejected / offer), enabling future response-rate analytics
- **Follow-up automation** — 7-day follow-up date written at application time; surfaced automatically each run

**Visual suggestion:** three-gate funnel diagram (wide at top, narrow at bottom), with token cost annotations

---

## Slide 5 — Demo & Results

**Title:** Live Terminal Dashboard

**What the TUI shows (`python tui.py --demo`):**
- Full-screen pipeline monitor with staged reveals per job
- Liveness → Salary → Scoring (live bar charts per sub-score) → Materials
- Running footer: scanned / dropped at liveness / scored / materials generated
- Every value rendered passes through the same Pydantic models the pipeline uses — not a separate mockup

**Sample run over 3 jobs:**
- **Stripe** — active, $180k–$240k/yr, score 8/10 (high fit) → resume + cover letter generated
- **Acme Corp** — expired at liveness → dropped, scorer never called
- **Vercel** — active, $130k–$170k/yr, score 7/10 (medium fit) → resume + cover letter generated

**Tech stack:**
`openai` · `pydantic` · `sqlalchemy` · `playwright` · `rich` · `requests`

**Source:** `github.com/jaimalharsk/dev-lab` → `experiments/local-ai/remote-job-autoapply-mvp`

**Visual suggestion:** screenshot of the running TUI from your demo recording
