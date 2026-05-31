# Week 5 · Day 4 — AI Feedback Generator

Generate human-like interview feedback and a post-session **AI Interview Coach** plan.

## Per-answer feedback

After each answer, `feedback_generator.py` produces:

| Field | Description |
|-------|-------------|
| `human_feedback` | 2–4 natural coach sentences |
| `strengths` | What went well |
| `weaknesses` | Gaps (e.g. missing examples, filler words) |
| `improvement_suggestions` | Actionable tips (delivery, structure, content) |

Example tone:

> “Your answer was technically correct, but lacked real-world examples.”  
> “Try improving eye contact and reducing filler words.”

Uses **OpenAI** when `OPENAI_API_KEY` is set; otherwise heuristic templates from scores and keywords.

## Post-interview AI Coach

When the session completes, `generate_coach_report()` returns:

- `overview` — encouraging summary
- `strengths` / `weaknesses` — session-level
- `improvement_roadmap` — phased plan (Week 1–3) with actions
- `learning_topics` — topics to study
- `practice_questions` — suggested questions from the question bank

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/interview/session/{id}/answer` | Includes enriched turn + `coach_report` when done |
| GET | `/api/interview/session/{id}/coach` | Fetch or regenerate coach plan |

## Frontend

`/interview` — feedback card shows coach quotes, weaknesses, and suggestions; completion screen shows the full **AI Interview Coach** panel.

## Module

`backend/app/interview/feedback_generator.py`
