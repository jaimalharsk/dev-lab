# Demo Video Script — 3 Minutes

**Recording tips:** Use a screen recorder (OBS, Loom, QuickTime). Keep terminal font at 16pt+. Have all tabs open before you hit record.

---

## 0:00–0:30 — Problem statement (talking over a static slide or blank terminal)

> "Job applications are time-consuming and mostly wasted effort — you spend an hour tailoring a resume for a listing that was already closed, or that's a poor fit. And if you try to automate it with an LLM, you get unstructured text back that you can't actually use in a pipeline. This project solves both problems."

**On screen:** Show `presentation.html` page 1 (open in browser, zoomed in on the pipeline diagram).

---

## 0:30–1:00 — Show the structured output schemas

> "The core idea is that every AI step in the pipeline returns a validated Pydantic model — not a string, not a dict. If the model returns something that doesn't fit the schema, the pipeline fails loudly instead of silently passing bad data downstream."

**On screen:** Open `ai/schemas.py` in your editor.

Highlight and read out:
- `JobRelevanceResult` — point to the four sub-score fields and the `@computed_field` score
- Say: *"The LLM gives us four scores. The composite is computed in Python — the model never touches the weights."*
- `CoverLetter` — point to opening/body/closing
- `LivenessResult` — point to the Literal type on status

---

## 1:00–1:30 — Walk through the pipeline flow

> "Before we ever call the LLM to score a job, we check if the posting is still live."

**On screen:** Open `scrapers/liveness.py`. Point to the `_EXPIRED_PATTERNS` list at the top.

> "These regex patterns are ported from an open-source project called career-ops. If the page has any of these phrases, or returns a 404, we drop the listing from the database immediately — no AI tokens spent."

Switch to `app.py`. Scroll to the `apply_pipeline` function. Point to the liveness check block:

> "You can see the flow here — liveness check first. If expired, we delete the job and continue. If active, we call the scorer, which returns a `JobRelevanceResult`. We use `result.score` — the computed composite — to decide whether to proceed."

Point to the follow-up block at the bottom:

> "Every application also records a follow-up date seven days out. At the end of the run, the pipeline prints anything that's overdue."

---

## 1:30–2:15 — Show the sample data

> "I can't run a live scrape in three minutes, so I'll show the sample dataset instead — this represents what the pipeline produces."

**On screen:** Open `data/sample_jobs.json` in your editor or browser.

Walk through the three entries:

1. **Stripe** — *"Role match 0.88, level fit 0.82, composite score 8/10. High fit. The pipeline would generate a resume and cover letter for this one."* Scroll down to show the `tailored_resume` and `cover_letter` objects. *"Notice cover letter is split into opening, body, closing — structured, not a blob of text."*

2. **Acme Corp** — *"This one never reaches the scorer. Liveness check flagged it as expired — pattern matched 'no longer available'. Listing is deleted from the DB."*

3. **Vercel** — *"Score 7/10, medium fit. role_match is lower because the role is advocacy, not pure engineering. The pipeline still generates materials since 7 meets our threshold."*

---

## 2:15–2:45 — Show the presentation PDF

**On screen:** Switch to `presentation.html` open in browser. Scroll slowly through both pages.

> "This is the project write-up — two pages covering the architecture, the schema design decisions, and a sample output table. To export it as a PDF: File → Print → Save as PDF."

Briefly highlight the scoring formula on page 1 and the design decisions table on page 2.

---

## 2:45–3:00 — Wrap up

> "To summarise: a multi-step LLM pipeline where every output is validated. Liveness check before scoring saves tokens and prevents applying to dead listings. Weighted sub-scores keep the arithmetic in code, not in the prompt. And all outputs — scoring, resume, cover letter — are typed Pydantic models that fail loudly on bad data."

> "Source code is at github.com/jaimalharsk/dev-lab under experiments/local-ai/remote-job-autoapply-mvp."

**On screen:** Show the GitHub repo page.

---

## Before you record — checklist

- [ ] Terminal font size 16pt or larger
- [ ] `ai/schemas.py` open in editor
- [ ] `scrapers/liveness.py` open in editor  
- [ ] `app.py` open in editor, scrolled to `apply_pipeline`
- [ ] `data/sample_jobs.json` open in editor
- [ ] `presentation.html` open in browser (full screen, zoomed to 110%)
- [ ] GitHub repo open in browser tab
- [ ] Microphone tested
- [ ] Do one dry run at 1.0x speed to check timing
