# ML Model Artifacts (Day 5+)

Train models:

```bash
python datasets/scripts/train_models.py
```

## Files (generated locally, gitignored)

| File | Model |
|------|--------|
| `performance_random_forest.joblib` | RF → performance % |
| `performance_xgboost.joblib` | XGBoost → performance % |
| `pass_fail_random_forest.joblib` | RF → at-risk (0/1) |
| `pass_fail_xgboost.joblib` | XGBoost → at-risk |
| `training_metrics.json` | Evaluation metrics |
| `best_model.json` | Which model FastAPI uses |

## API

`POST /api/predict` loads the best regression model from `best_model.json`.

If no `.joblib` files exist, the API falls back to a heuristic formula.
