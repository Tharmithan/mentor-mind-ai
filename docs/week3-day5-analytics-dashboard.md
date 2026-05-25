# Week 3 Day 5 — Analytics Dashboard

## Goal

Visually impressive analytics with Recharts + Chart.js and an **AI Risk Meter**.

## Cards

| Card | Source |
|------|--------|
| AI Score | `analytics.cards.ai_score` |
| Risk Level | low / medium / high |
| Performance Trend | Week-over-week delta % |
| Study Streak | Consecutive study days |

## Charts

| Chart | Library | Data |
|-------|---------|------|
| Weekly Progress | Recharts | `weekly_progress` |
| Subject Comparison | Chart.js | `subject_comparison` |
| Confidence Trends | Chart.js | `confidence_trends` |

## AI Risk Meter

- **Burnout risk** — sleep + study load
- **Exam failure risk** — performance + ML at-risk signal
- **Low engagement** — attendance + study hours

## API

`GET /api/dashboard` — includes `analytics` object.

## Frontend

- `AnalyticsDashboard.tsx` — full analytics section
- `AIRiskMeter.tsx` — risk bars
- `SubjectComparisonChart.tsx` / `ConfidenceTrendChart.tsx` — Chart.js
