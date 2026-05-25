# Day 5 — Build First ML Model

**Goal:** Train simple ML models (no deep learning) to predict performance score and pass/fail.

---

## Models trained

| Algorithm | Regression (score) | Classification (pass/fail) |
|-----------|-------------------|---------------------------|
| **Random Forest** | `RandomForestRegressor` | `RandomForestClassifier` |
| **XGBoost** | `XGBRegressor` | `XGBClassifier` |

---

## Targets

| Task | Column | Meaning |
|------|--------|---------|
| Performance score | `performance_pct` | 0–100% |
| Pass / fail | `at_risk` | 0 = pass, 1 = at-risk (fail) |

---

## Pipeline

```bash
python datasets/scripts/clean_data.py
python datasets/scripts/feature_engineering.py   # optional
python datasets/scripts/train_models.py
```

Uses `train_test_split` (80/20) and `joblib.dump()` → `ml-models/`.

---

## Saved artifacts (`ml-models/`)

| File | Description |
|------|-------------|
| `performance_random_forest.joblib` | RF regression |
| `performance_xgboost.joblib` | XGB regression |
| `pass_fail_random_forest.joblib` | RF classification |
| `pass_fail_xgboost.joblib` | XGB classification |
| `training_metrics.json` | MAE, R², accuracy, F1 |
| `best_model.json` | Production model selection |

FastAPI `/api/predict` loads the best model automatically (falls back to heuristic if missing).

---

## Checklist

- [x] `train_test_split`
- [x] `RandomForestClassifier` + `RandomForestRegressor`
- [x] `XGBClassifier` + `XGBRegressor`
- [x] `joblib.dump()`
- [x] Predict performance score + pass/fail
- [x] Backend integration

---

## macOS note (XGBoost)

If XGBoost fails to load:

```bash
brew install libomp
pip install xgboost
```

Training still completes with **Random Forest** if XGBoost is unavailable.

## Metrics note

Behavioral-only features (study hours, attendance, readiness) predict **without prior grades**, so R² is modest — that is expected. Grade-inclusive models score much higher (see Day 4 `performance_ml_ready.csv`).

---

## Next

Hyperparameter tuning, confusion matrix plots, model card in README.
