# Week 3 Day 7 — Backend Integration + APIs

## Goal

Connect all Week 3 AI modules behind a unified API surface.

## Backend structure

```
backend/app/
├── routes/ai_platform.py
├── ai/              → predict, explain, insights
├── recommendation/  → engine, planner, service
├── analytics/       → risk meter, charts data
└── models/          → Pydantic schemas
```

## Canonical routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/predict` | ML performance prediction |
| POST | `/predict/explain` | Predict + SHAP explanations |
| POST | `/recommend` | Recommendations + optional study plan |
| GET | `/analytics` | Analytics cards, risk meter, chart data |
| GET | `/insights` | AI insights + trends |
| GET | `/api/ai/status` | All modules connected? |

Legacy routes (`/api/dashboard`, `/api/study-planner`, etc.) remain for the frontend.

## Test

```bash
curl http://localhost:8000/api/ai/status
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"study_hours":5,"attendance":82,"sleep_hours":7}'
curl -X POST http://localhost:8000/api/recommend -H "Content-Type: application/json" \
  -d '{"study_hours":3,"attendance_pct":72}'
curl http://localhost:8000/api/analytics
curl http://localhost:8000/api/insights
```
