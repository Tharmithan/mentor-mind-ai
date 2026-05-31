# Week 7 · Day 2 — Long-Term Memory System

**Goal:** AI remembers user progress across sessions — chat history, study plans, interview scores, and career goals.

---

## Example

**Last month:** User struggled with Machine Learning (48%).

**This month:** AI says:

> Your **Machine Learning** performance improved by **15%** since last month.

Study and Career agents prepend progress insights automatically.

---

## Architecture

```
Chat sessions ──┐
Agent sessions ─┼──► LongTermMemoryService.sync_user()
Interview JSON ─┤         ↓
Study plans ────┘    uploads/long_term_memory/{user_id}.json
                              ↓
                    ProgressTracker (month-over-month deltas)
                              ↓
                    ContextRetriever → agents / coach UI
```

---

## Memory storage

| Type | Stored fields |
|------|----------------|
| **Conversations** | session_id, summary, topics, agent |
| **Study plans** | subject, summary, plan_id |
| **Interview scores** | overall, technical, session_id |
| **Career goals** | goal, active flag, timestamp |
| **Subject snapshots** | monthly scores for progress deltas |

---

## Backend layout

```
backend/app/memory/
├── store.py       # JSON memory database
├── service.py     # Sync, record, orchestrate
├── progress.py    # Month-over-month deltas + insights
└── retrieval.py   # Context retrieval for agents
```

---

## API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/memory/{user_id}` | Full memory record |
| GET | `/api/memory/{user_id}/context?query=ml` | Retrieved context |
| GET | `/api/memory/{user_id}/progress` | Progress deltas + narrative |
| POST | `/api/memory/{user_id}/sync` | Sync from file stores |
| POST | `/api/memory/{user_id}/snapshot` | Record score snapshot |
| GET | `/api/memory/demo/progress` | Demo user progress |

---

## Integrations

- **Agent Manager** — records every agent turn; prepends progress insight for Study/Career
- **Profile Engine** — syncs memory on profile build
- **AI Coach** — Long-Term Memory panel with % deltas

---

## Smoke test

```bash
cd backend
python -c "
from app.memory.service import LongTermMemoryService
from app.recommendation.engine import get_recommendation_engine

scores = get_recommendation_engine().default_subject_scores()
scores['Machine Learning'] = 63
prog = LongTermMemoryService.get_progress('demo-user-001', scores)
print(prog.narrative)
for d in prog.deltas[:3]:
    print(d.subject, d.delta_pct)
"
```

Open **http://localhost:3000/coach** → **Long-Term Memory** panel.
