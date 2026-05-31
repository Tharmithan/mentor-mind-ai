# Week 7 · Day 6 — Monitoring & Feedback Loop

Make AI improve continuously by collecting ratings, monitoring predictions, and closing the loop into recommendations.

## What you built

| Capability | Implementation |
|------------|----------------|
| **Feedback system** | `POST /api/monitoring/feedback` — ratings for recommendations, predictions, interviews |
| **Model monitoring** | Auto-log every `/predict` call; track MAE and drift when users submit actual scores |
| **User satisfaction** | Composite satisfaction score + trend (improving / stable / declining) |
| **Continuous improvement** | Negative feedback downranks resources in `PersonalizedRecommender` |

## Example flow

1. User clicks **Not useful** on a recommendation → stored as `category: recommendation`
2. `ImprovementLoop` downranks that title/subject/format
3. Next `GET /api/personalization/recommendations/{user_id}` returns adjusted list
4. Coach dashboard shows updated satisfaction + improvement insights

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/monitoring/feedback` | Submit rating (1–5) + comment |
| GET | `/api/monitoring/feedback/{user_id}` | User feedback history |
| GET | `/api/monitoring/satisfaction/{user_id}` | Satisfaction summary |
| GET | `/api/monitoring/model-metrics` | Prediction monitoring (MAE, drift) |
| GET | `/api/monitoring/improvements/{user_id}` | Improvement loop insights |
| GET | `/api/monitoring/dashboard/{user_id}` | Full dashboard |
| GET | `/api/monitoring/demo` | Demo user dashboard |

### Submit feedback

```bash
curl -X POST http://localhost:8000/api/monitoring/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user-001",
    "category": "recommendation",
    "target_id": "LeetCode — Arrays",
    "rating": 1,
    "helpful": false,
    "comment": "Recommendation was not useful"
  }'
```

### Prediction accuracy feedback

```bash
curl -X POST http://localhost:8000/api/monitoring/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "category": "prediction",
    "rating": 2,
    "metadata": { "actual_score": 72, "predicted_score": 85 }
  }'
```

## Frontend

- **Coach dashboard** → **Monitoring & Feedback** panel
- **Personalized For You** → thumbs up/down on each resource
- **AI Performance Predictor** → rate prediction + optional actual score

## Storage

```
uploads/monitoring/
  feedback.json         # all user ratings
  prediction_logs.json  # logged predictions + actuals
```

## Architecture

```
User rating → FeedbackCollector → SatisfactionTracker
                    ↓
              ImprovementLoop → PersonalizedRecommender (filter)
                    ↓
              ModelMonitor ← PredictionService (auto-log)
```

## Recruiter talking points

1. **Closed feedback loop** — not just collecting data; recommendations change based on ratings
2. **Model observability** — MAE, drift status, prediction volume
3. **Multi-channel feedback** — recommendations, predictions, interviews, general
4. **Production pattern** — file-backed store with optional DB path later

## Next steps

- Wire interview session end-screen to `category: interview` feedback
- Alert when `drift_status === "alert"` in MLOps panel
- Batch export feedback for fine-tuning / RLHF
