# Week 3 Day 3 — Recommendation Engine

## Goal

Personalized AI that recommends **what to study**, **weak subjects**, and **revision order**, plus an **AI Daily Study Planner**.

## Techniques

| Layer | Implementation |
|-------|----------------|
| **Rule-based** | Thresholds on scores, attendance, sleep, study hours |
| **Collaborative filtering** | Cosine similarity vs UCI student cohort (`student_performance_cleaned.csv`) |

## Example

Low math (58%) + low attendance (72%) →

> **Focus on Algebra revision this week.**

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recommendations` | List recommendations (engine-powered fallback) |
| GET/POST | `/api/recommendations/personalized` | Weak subjects + revision order + insights |
| GET/POST | `/api/study-planner` | Daily timetable + focus areas + summary |

### POST body example

```json
{
  "study_hours": 3,
  "attendance_pct": 72,
  "sleep_hours": 6.5,
  "subject_scores": [
    { "subject": "Mathematics", "score": 58 },
    { "subject": "Portuguese", "score": 72 }
  ],
  "risk_level": "high"
}
```

## Frontend

- `StudyPlannerPanel` on dashboard — loads `/api/study-planner`
- AI Suggestions section uses engine via `/api/recommendations`

## Code

- `backend/app/ml/recommendation_engine.py` — core logic
- `backend/app/services/study_planner_service.py` — API layer
- `backend/app/routes/study_planner.py` — routes
