# Day 4 — Feature Engineering

**Goal:** Create better input features, test importance, remove weak predictors.

---

## Custom features

| Feature | Description |
|---------|-------------|
| `consistency_score` | Grade stability across G1, G2, G3 (low variance = high consistency) |
| `productivity_index` | Study output per failure: `study_hours × attendance / (failures + 1)` |
| `exam_readiness_score` | Weighted readiness formula |
| `assignment_completion_score` | `100 − past_failures × 25` |
| `grade_momentum_score` | Improvement from G1 → final grade |

### Exam readiness formula

```python
study_scaled = scale(study_hours, 0, 6)   # 0–100
exam_readiness_score = (
    study_scaled * 0.4
    + attendance_pct * 0.3
    + assignment_completion_score * 0.3
)
```

---

## Feature selection

1. Train **Random Forest** on all candidate features  
2. Rank by **feature importance**  
3. **Drop weak** features below 2% of max importance  
4. Export selected set to `datasets/final/`

---

## Commands

```bash
python datasets/scripts/clean_data.py              # prerequisite
python datasets/scripts/feature_engineering.py
jupyter notebook notebooks/04_feature_engineering.ipynb
```

---

## Outputs (`datasets/final/`)

| File | Description |
|------|-------------|
| `performance_features_full.csv` | Base + all engineered features |
| `performance_ml_ready.csv` | Selected features + target |
| `train.csv` / `test.csv` | 80/20 split (grade-inclusive) |
| `performance_ml_ready_behavioral.csv` | Study/attendance/readiness — **for API prediction** |
| `train_behavioral.csv` | Behavioral train split |
| `feature_importance.json` | Rankings + dropped list |
| `feature_engineering_report.md` | Human-readable summary |

---

## Checklist

- [x] Create custom features (consistency, productivity, exam readiness)
- [x] Test feature importance (Random Forest)
- [x] Remove weak features
- [x] Export ML-ready `final/` dataset

---

## Next (Day 5)

Train first ML model (XGBoost / Random Forest) using `final/train.csv`.
