# Week 6 · Day 5 — Personalized Learning Planner

**Goal:** Generate **complete learning roadmaps** from career goals — month-by-month topics, milestones, progress tracking, and weekly plans.

---

## Example

```
User Goal: Become an AI Engineer

Month 1: Python, Statistics
Month 2: Machine Learning
Month 3: Deep Learning
Month 4: NLP
Month 5: Production AI
Month 6: Portfolio & Interviews
```

Each month includes goals, resources, and a milestone to mark complete.

---

## Features

| Feature | Description |
|---------|-------------|
| **Roadmap generator** | 4–6 month plans for AI Engineer, Data Scientist, MLOps, SWE |
| **Progress tracking** | Persisted plans with % complete, current month/week |
| **Goal milestones** | Mark monthly milestones done → auto-advance |
| **Weekly planning** | 4-week breakdown per month with tasks and hours |

---

## Backend

```
backend/app/planner/
├── roadmaps.py         # Monthly templates (AI Engineer = user example)
├── generator.py        # Roadmap from natural-language goal
├── weekly_planner.py   # Week 1–4 tasks per month
└── progress_store.py   # Plans → uploads/learning_plans/

backend/app/routes/learning_planner.py
backend/app/agents/study_agent.py  # Chat: "Become an AI Engineer"
```

---

## API

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/learning-planner/roadmap` | Preview roadmap (no save) |
| `POST` | `/api/learning-planner/plans` | Create tracked plan |
| `GET` | `/api/learning-planner/plans/{id}` | Get plan + progress |
| `PATCH` | `/api/learning-planner/plans/{id}/progress` | Update milestone / week |
| `GET` | `/api/learning-planner/plans/{id}/weekly` | Weekly plan markdown |

---

## Frontend

- **`/planner`** — `LearningPlannerPanel` with goal input, month cards, milestones, weekly view
- Sidebar: **Learning Planner**

---

## Try it

```bash
# Generate AI Engineer roadmap
curl -s -X POST http://127.0.0.1:8000/api/learning-planner/roadmap \
  -H "Content-Type: application/json" \
  -d '{"goal":"Become an AI Engineer","hours_per_week":10}' | jq '.months[] | {month, title, topics: [.topics[].name]}'

# Via chat
curl -s -X POST http://127.0.0.1:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Become an AI Engineer — create my learning plan"}' | jq .answer
```

Open **http://localhost:3000/planner** → select goal → **Start tracking**.

---

## Next

- Calendar sync / reminders
- Link weekly plan to Study Agent daily recommendations
- Dashboard widget for active plan progress
