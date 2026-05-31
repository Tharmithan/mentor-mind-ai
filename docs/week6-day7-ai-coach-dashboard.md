# Week 6 · Day 7 — AI Coach Dashboard

**Goal:** Premium unified dashboard aggregating all Week 6 AI agents into scores, charts, skill gaps, and weekly progress reports.

---

## Dashboard cards

| Card | Source |
|------|--------|
| Learning Score | Dashboard performance + study hours |
| Interview Score | Interview session averages |
| Career Readiness | Skill gap analyzer |
| Resume Score | Latest resume ATS analysis |
| AI Recommendations | Count of agent-generated action items |

---

## Charts

| Chart | Data |
|-------|------|
| Skill Growth | 5-week average skill proficiency trend |
| Learning Progress | Weekly performance scores |
| Interview Improvement | Mock interview score trend |
| Career Readiness Trend | Readiness % over 5 weeks |

---

## Extra features

### Skill Gap Analyzer

Shows **Current Skills → Target Role → Missing Skills** with detailed gap priorities.

Example:
- Current: Python, SQL
- Target: AI Engineer
- Missing: Deep Learning, MLOps, NLP

### AI Weekly Progress Report

Auto-generated each load:
- **Achievements** — study hours, score deltas, completed goals
- **Weaknesses** — weak subjects, high-priority skill gaps
- **Next week's plan** — study focus, mock interviews, resume updates

---

## API

```http
GET /api/coach/overview?target_career=AI Engineer&session_id=abc123
GET /api/coach/weekly-report?session_id=abc123
```

---

## Frontend

- Route: **`/coach`** — AI Coach Dashboard (sidebar: **AI Coach**)
- Components: `frontend/src/components/coach/`

---

## Week 6 complete

| Area | Status |
|------|--------|
| Study Agent | ✔ |
| Career Agent | ✔ |
| Resume Agent | ✔ |
| Interview Agent | ✔ |
| Multi-Agent Collaboration | ✔ |
| Personalized Roadmaps | ✔ |
| Career Guidance | ✔ |
| Resume Analysis | ✔ |
| Skill Gap Detection | ✔ |
| AI Coach Dashboard | ✔ |

---

## Smoke test

```bash
cd backend
python -c "
import asyncio
from app.services.coach_service import CoachService
async def main():
    r = await CoachService.get_overview(None, target_career='AI Engineer')
    assert len(r.scores) == 5
    print('OK', r.target_career)
asyncio.run(main())
"
```

Open **http://localhost:3000/coach** with backend on `:8000`.
