# Demo Video Script — 3 Minutes

**Recording tips:** Use a screen recorder (OBS, Loom, QuickTime). Keep terminal font at 16pt+. Have everything below open and ready before you hit record. The TUI runs in full-screen mode — start the recording, then launch it.

---

## 0:00–0:25 — Problem statement

> "Job applications are time-consuming and mostly wasted effort — you spend an hour tailoring a resume for a listing that's already closed, or that's a poor fit. And if you try to automate it with an LLM, you get unstructured text back that you can't actually use in a pipeline. This project fixes both: it filters dead listings before spending any tokens, and every AI output is a validated, typed object."

**On screen:** `presentation.html` page 1, zoomed in on the pipeline diagram.

---

## 0:25–0:55 — Show the schemas (the foundation of the whole pipeline)

> "Every AI step returns a Pydantic model, not a string. If the model returns something that doesn't fit the schema, the pipeline fails loudly instead of silently passing bad data downstream."

**On screen:** Open `ai/schemas.py`.

- Point to `JobRelevanceResult` — the four sub-score fields and the `@computed_field score`
- *"The LLM scores four dimensions. The composite is computed in Python — the model never touches the weights."*
- Point to `LivenessResult` and `CoverLetter`

---

## 0:55–2:30 — Run the live TUI demo (the centerpiece)

> "Let me show you the pipeline running. This terminal dashboard replays a sample dataset through every stage, live."

**On screen:** Run:

```bash
python tui.py --demo
```

Narrate as it plays — the dashboard does the pacing for you (~1.7s per reveal):

- **Job 1 (Stripe)** — *"First, a liveness check — before we spend a single token, we confirm the posting is actually live. This one's active. Next, salary extraction: `SalaryRange` comes back with $180k–$240k/yr, disclosed, clears the floor. Now it scores across four dimensions — role match, level fit, growth potential, remote alignment — each rendered as its own bar. Composite: 8 out of 10, high fit. Because it clears the threshold, the pipeline generates a tailored resume summary and a structured cover letter — opening, body, closing as separate fields, not a wall of text."*

- **Job 2 (Acme Corp)** — *"Watch this one — the liveness check catches a closed posting immediately. `LivenessResult` comes back `expired`, the job is deleted from the database, and the scorer is never even called. Zero tokens wasted on a dead listing."*

- **Job 3 (Vercel)** — *"Score of 7, medium fit — role match is lower because it's an advocacy role rather than pure engineering, but level fit and growth potential are both strong. Salary is $130k–$170k, clears the floor. Still clears the threshold, so materials get generated."*

- **Footer** — *"This running counter — scanned, dropped at liveness, scored, materials generated — updates live as each job clears the pipeline."*

Let it finish on the green "Pipeline complete" panel.

> "Everything you just saw — every score, every bar, every line of that cover letter — passed through Pydantic validation before it was rendered. The dashboard is a consumer of the same structured output the pipeline produces, not a separate mockup."

---

## 2:30–2:50 — Show the orchestration code

**On screen:** Open `app.py`, scroll to `apply_pipeline`.

> "Here's the actual flow driving what you just watched — liveness check first, then `result.score` from the validated `JobRelevanceResult` decides whether to proceed. Every application also gets a follow-up date seven days out, surfaced automatically at the end of each run."

---

## 2:50–3:00 — Wrap up

> "A multi-step LLM pipeline where every output is a validated, typed model — liveness checks save tokens, weighted sub-scores keep the math in code, and nothing downstream ever sees malformed data. Source is at github.com/jaimalharsk/dev-lab, under experiments/local-ai/remote-job-autoapply-mvp."

**On screen:** GitHub repo page.

---

## Before you record — checklist

- [ ] Terminal font size 16pt or larger, full-screen terminal window
- [ ] `python tui.py --demo` tested once at full speed (total runtime ≈ 34–36s)
- [ ] `ai/schemas.py` open in editor
- [ ] `app.py` open in editor, scrolled to `apply_pipeline`
- [ ] `presentation.html` open in browser (page 1 visible, zoomed to 110%)
- [ ] GitHub repo open in a browser tab
- [ ] Microphone tested
- [ ] One full dry run with narration to check total timing fits within 3 minutes
