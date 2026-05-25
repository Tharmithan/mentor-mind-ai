# MentorMind Backend

## Week 3 AI platform structure

```
backend/app/
├── routes/           # FastAPI routers
│   └── ai_platform.py   # POST /predict, /recommend, GET /analytics, /insights
├── ai/               # ML predict, explain, insights
├── recommendation/   # Study planner + collaborative filtering
├── analytics/        # Risk meter, dashboard analytics
└── models/           # Pydantic request/response schemas
```

## Canonical API (Day 7)

| Method | Route | Module |
|--------|-------|--------|
| POST | `/predict` | ai |
| POST | `/recommend` | recommendation |
| GET | `/analytics` | analytics |
| GET | `/insights` | ai |
| GET | `/api/ai/status` | platform health |

Also at `/api/*` prefix.

## Run

```bash
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
```
