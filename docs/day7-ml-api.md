# Day 7 — ML API (Frontend ↔ Backend)

**Goal:** Frontend sends data → trained AI predicts performance.

---

## Endpoint

```
POST /api/predict
POST /predict          # same handler (alias)
```

---

## Request

```json
{
  "study_hours": 5,
  "attendance": 82,
  "sleep_hours": 7
}
```

| Field | Type | Description |
|-------|------|-------------|
| `study_hours` | float | 0–24 |
| `attendance` | float | Attendance % (0–100) |
| `sleep_hours` | float | Maps to wellness proxy for ML model |
| `prior_score` | float | Optional, default 70 |
| `quizzes_completed` | int | Optional, default 10 |

---

## Response

```json
{
  "prediction": "High Performance",
  "confidence": 92,
  "predicted_score": 78.5,
  "risk_level": "low",
  "recommendation": "On track — maintain current study pace.",
  "model_version": "random_forest-v1.0"
}
```

| `prediction` | When |
|--------------|------|
| High Performance | score ≥ 75% |
| Medium Performance | score ≥ 60% |
| At Risk | at-risk model or score < 50% |
| Low Performance | otherwise |

---

## Try it

```bash
# Backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# curl
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"study_hours": 5, "attendance": 82, "sleep_hours": 7}'
```

**Frontend:** Dashboard → **AI Performance Predictor** panel (live form).

---

## Model

Loads `ml-models/performance_random_forest.joblib` from Day 5 training.  
Falls back to heuristic if models missing.

---

## Checklist

- [x] POST /predict
- [x] JSON input (study_hours, attendance, sleep_hours)
- [x] JSON output (prediction, confidence)
- [x] ML model wired
- [x] Dashboard UI connected
