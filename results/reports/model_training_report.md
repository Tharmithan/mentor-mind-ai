# Model Training Report

**Week 3 Day 2 — XGBoost Hyperparameter Tuning**

*Generated: 2026-05-25T10:45:58.535419+00:00*

## Executive summary

Tuned XGBoost with **random_tuned** search. Test F1 improved from **0.588** to **0.630** (+7.2%). Accuracy: **58.4%** → **61.2%** (+4.9%).

## Best parameters

```json
{
  "colsample_bytree": 0.8018,
  "learning_rate": 0.1095,
  "max_depth": 4,
  "n_estimators": 133,
  "subsample": 0.8593
}
```

| Parameter | Baseline | Best tuned |
|-----------|----------|------------|
| n_estimators | 200 | 133 |
| max_depth | 6 | 4 |
| learning_rate | 0.08 | 0.1095 |
| subsample | — | 0.8593 |
| colsample_bytree | — | 0.8018 |

## Search methods

### GridSearchCV

- Param grid: `n_estimators`, `max_depth`, `learning_rate` (27 combos)
- Best CV F1: **0.6282**
- Search time: **4.335s**
- Test F1 after refit: **0.5943**

### RandomizedSearchCV

- Iterations: **24**
- Best CV F1: **0.6192**
- Search time: **1.06s**
- Test F1 after refit: **0.6301**

## Before vs after (test set)

| Metric | Baseline | Best tuned | Δ |
|--------|----------|------------|---|
| Accuracy | 58.4% | 61.2% | +4.92% |
| Precision | 62.6% | 64.5% | +2.97% |
| Recall | 55.4% | 61.6% | +11.29% |
| F1 | 0.5877 | 0.6301 | +7.21% |
| R² (regression) | -0.0365 | 0.0107 | -129.32% |

## Training time

| Stage | Seconds |
|-------|---------|
| Baseline fit | 0.516 |
| GridSearchCV | 4.335 |
| RandomizedSearchCV | 1.06 |
| Best tuned refit | 0.255 |
| **Total pipeline** | **6.58** |

## Saved artifacts

- `results/metrics/hyperparameter_tuning.json`
- `results/graphs/tuning_before_after.png`
- `ml-models/saved_models/performance_model_v3.joblib` (if tuned beats baseline)
- `ml-models/saved_models/pass_fail_model_v3.joblib`

## Note

Day 1 winner was Random Forest (F1 ~0.63). This report documents XGBoost tuning; deploy tuned XGBoost only if it exceeds your production threshold.
