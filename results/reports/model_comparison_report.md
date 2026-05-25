# Week 3 Day 1 — Model Comparison Report

*Generated: 2026-05-25T10:40:50.753797+00:00*

## Best model (classification F1)

**Random Forest** — F1 0.6256, Accuracy 62.2%, Train time 0.326s

## Comparison table

| Model | Accuracy | Precision | Recall | F1 | R² | Train (s) |
|-------|----------|-----------|--------|-----|-----|-----------|
| random_forest | 62.2% | 66.7% | 58.9% | 0.63 | 0.009 | 0.326 |
| gradient_boosting | 60.8% | 65.0% | 58.0% | 0.61 | -0.032 | 0.269 |
| xgboost | 58.4% | 62.6% | 55.4% | 0.59 | -0.036 | 0.502 |
| lightgbm | 59.3% | 62.4% | 60.7% | 0.62 | 0.027 | 0.615 |
| catboost | 60.3% | 63.5% | 60.7% | 0.62 | 0.032 | 0.257 |

## Top features (best model)

- **Wellness**: 23.85%
- **Productivity**: 20.78%
- **Exam readiness**: 18.61%
- **Attendance**: 15.02%
- **Past failures**: 10.13%

## Graphs

- `results/graphs/model_comparison_overview.png`
- `results/graphs/model_comparison_r2.png`
- `results/graphs/feature_importance_best.png`

## Saved artifact

`ml-models/saved_models/performance_model_v2.joblib`
