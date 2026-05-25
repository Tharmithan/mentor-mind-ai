# Week 3 Day 6 — Model Explainability

## Goal

Explain **why** the AI made each prediction — recruiter-ready explainable AI.

## Techniques

| Method | When used |
|--------|-----------|
| **SHAP** (TreeExplainer) | Trained tree models + `shap` installed |
| **Feature importance** | Fallback weighted by feature deviation |
| **Global SHAP** | Batch script on cohort |

## Example output

> Low attendance contributed 38% to predicted low performance.

## API

| Endpoint | Description |
|----------|-------------|
| `POST /api/predict/explain` | Predict + SHAP explanations |
| `GET /api/explain/global` | Global feature rankings |

## Generate SHAP plots

```bash
pip install shap
python datasets/scripts/explain_model.py
```

Outputs:
- `results/graphs/shap_summary.png`
- `results/graphs/shap_feature_importance.png`
- `results/metrics/shap_global.json`
- `results/reports/model_explainability_report.md`

## Frontend

`AIExplanationPanel` — contribution bar chart (Recharts) + human sentences under ML Predict.
