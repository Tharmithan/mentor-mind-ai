# ML Experiment Results

Week 3+ model training outputs.

```
results/
├── metrics/     # JSON metrics (accuracy, F1, train time, feature importance)
├── graphs/      # Comparison charts (PNG)
└── reports/     # Markdown summaries for recruiters / docs
```

## Generate

```bash
cd /path/to/MentorMindAi
python datasets/scripts/compare_models.py   # Day 1
python datasets/scripts/tune_hyperparameters.py   # Day 2
```

Recommendation engine (Day 3): `POST /api/study-planner` — see `docs/week3-day3-recommendation-engine.md`

AI insights (Day 4): `GET /api/insights` — see `docs/week3-day4-ai-insights.md`

Requires cleaned data: `python datasets/scripts/clean_data.py` first.
