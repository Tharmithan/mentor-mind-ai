# Week 7 · Day 3 — AI Learning Analytics

**Goal:** Generate insights from user behavior — best study time, productivity patterns, weak areas, and burnout risk.

---

## AI detects

| Signal | How |
|--------|-----|
| **Best study time** | Preferred style + peak study hours by day |
| **Productivity patterns** | Hours/week, streak, weak-area focus |
| **Weak learning areas** | Subject scores + long-term memory deltas |
| **Burnout risk** | Sleep load, study intensity, performance |

---

## Dashboard features

| Feature | Metric |
|---------|--------|
| Learning efficiency | Performance × consistency − weak-subject penalty |
| Weekly growth | Performance trend + memory deltas |
| Subject mastery | beginner → developing → proficient → mastered |
| Progress trends | Multi-week score chart |

---

## Backend layout

```
backend/app/analytics/
├── learning_engine.py   # LearningAnalyticsEngine.analyze()
├── patterns.py          # PatternDetector — study time, productivity
└── service.py           # Risk meter (reused)

backend/app/routes/learning_analytics.py
backend/app/models/learning_analytics.py
```

---

## API

```http
GET /api/learning-analytics/demo
GET /api/learning-analytics/{user_id}
```

Response includes: `learning_efficiency`, `productivity_score`, `weekly_growth`, `subject_mastery`, `patterns`, `insights`, `risk_meter`.

---

## Frontend

**`/coach`** → **AI Learning Analytics** panel with:
- Efficiency & productivity scores
- Weekly growth + study hours charts
- Subject mastery cards with trends
- Pattern cards (best time, burnout, weak areas)
- AI insight feed

---

## Smoke test

```bash
cd backend
python -c "
import asyncio
from app.analytics.learning_engine import LearningAnalyticsEngine

async def main():
    r = await LearningAnalyticsEngine.analyze('demo-user-001')
    print('efficiency:', r.learning_efficiency)
    print('best time:', r.patterns.best_study_time)
    print('insights:', len(r.insights))

asyncio.run(main())
"
```

Open **http://localhost:3000/coach** → scroll to AI Learning Analytics.
