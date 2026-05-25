# Week 3 Day 2 — Hyperparameter Tuning

## Goal

Optimize XGBoost with **GridSearchCV** and **RandomizedSearchCV**.

## Parameters tuned

- `n_estimators`
- `max_depth`
- `learning_rate`
- (random search only) `subsample`, `colsample_bytree`

## Run

```bash
python datasets/scripts/tune_hyperparameters.py
```

## Outputs

| File | Description |
|------|-------------|
| `results/metrics/hyperparameter_tuning.json` | Baseline vs grid vs random vs best |
| `results/reports/model_training_report.md` | **Model Training Report** (bonus) |
| `results/graphs/tuning_before_after.png` | Before/after chart |
| `ml-models/saved_models/*_v3.joblib` | Saved if tuned beats baseline |

## Concepts

- **GridSearchCV** — exhaustive search over a small param grid (27 combos × 3-fold CV).
- **RandomizedSearchCV** — samples random combos from wider distributions (faster exploration).

Scoring metric: **F1** on `at_risk` classification (3-fold CV).
