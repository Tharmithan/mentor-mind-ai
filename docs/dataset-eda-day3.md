# Day 3 — Exploratory Data Analysis (EDA)

**Goal:** Understand patterns in data visually — recruiter-ready charts + AI Insights Report.

---

## Concepts

| Concept | Chart |
|---------|-------|
| **Correlation** | Heatmap (`05_correlation_heatmap.png`) |
| **Distributions** | Performance, study hours, attendance (`06_distributions.png`) |
| **Trends** | Regression lines on scatter plots |

---

## Required graphs

| Graph | File | Notes |
|-------|------|-------|
| Study hours vs marks | `01_study_hours_vs_marks.png` | Scatter + trend line |
| Attendance vs performance | `02_attendance_vs_performance.png` | Colored by at-risk |
| Sleep vs grades | `03_wellness_sleep_vs_grades.png` | `wellness_score` 1–5 as **sleep proxy** |
| Subject weaknesses | `04_subject_weaknesses.png` | Math vs Portuguese |

---

## AI Insights Report

Auto-generated from real data patterns:

- `datasets/processed/eda/ai_insights_report.md`
- `datasets/processed/eda/ai_insights_report.json`

Example insight format:

> Students with low wellness scores (≤2, sleep proxy) perform **18% worse** than high-wellness peers (≥4).

---

## Setup

```bash
pip install -r datasets/requirements-eda.txt
python datasets/scripts/clean_data.py      # if not done
python datasets/scripts/eda_analysis.py
```

**Jupyter / Colab:**

```bash
jupyter notebook notebooks/03_eda_ai_insights.ipynb
```

**Interactive Plotly dashboard:** open `datasets/processed/eda/07_eda_dashboard.html` in a browser.

---

## Checklist

- [x] Study hours vs marks
- [x] Attendance vs performance
- [x] Sleep/wellness proxy vs grades
- [x] Subject weaknesses
- [x] Correlation heatmap + distributions
- [x] matplotlib + seaborn + plotly
- [x] AI Insights Report
- [x] Jupyter notebook

---

## Next (Day 4)

Feature engineering → `datasets/final/` → train/test split → first ML model.
