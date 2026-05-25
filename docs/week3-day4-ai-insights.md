# Week 3 Day 4 — AI Insights System

## Goal

Human-like AI insights with trend analysis and performance summaries.

## Example insights

- "Your attendance dropped 12% this month."
- "Students with consistent sleep patterns perform better."
- "You are improving faster in coding subjects."

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/insights` | Insights + trends (query params for demo profile) |
| `POST /api/insights/generate` | Custom student profile |
| `GET /api/insights/summary` | Full payload with performance summary |
| `GET/POST /api/insights/report` | Natural language report |

## Outputs

- `results/metrics/ai_insights.json`
- `results/reports/ai_insights_summary.md`

## Advanced: LLM reports

Set in `.env`:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Without a key, reports use template-based natural language (no external API).

## Run

```bash
curl http://localhost:8000/api/insights
curl http://localhost:8000/api/insights/report
```
