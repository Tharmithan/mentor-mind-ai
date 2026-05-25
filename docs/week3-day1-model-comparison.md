# Week 3 Day 1 — Improve ML Models

## Goal

Train multiple boosters, compare accuracy / speed / feature importance, save the best model.

## Models

| Model | Library |
|-------|---------|
| Random Forest | scikit-learn |
| Gradient Boosting | scikit-learn |
| XGBoost | xgboost |
| LightGBM | lightgbm |
| CatBoost | catboost |

## Run

```bash
# Prerequisites
python datasets/scripts/clean_data.py

# Install optional boosters (recommended)
pip install lightgbm catboost matplotlib seaborn

# Week 3 Day 1 comparison
python datasets/scripts/compare_models.py
```

## Outputs

```
results/
├── metrics/model_comparison.json
├── graphs/
│   ├── model_comparison_overview.png
│   ├── model_comparison_r2.png
│   └── feature_importance_best.png
└── reports/model_comparison_report.md
```

Best models → `ml-models/saved_models/performance_model_v2.joblib` and `pass_fail_model_v2.joblib`.

API loads paths from `ml-models/best_model.json`.

## Selection criteria

**Classification F1** on `at_risk` (student pass/fail proxy). Regression R² reported for score prediction.
