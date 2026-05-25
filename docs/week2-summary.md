# Week 2 — Data & Machine Learning (Complete)

Professional ML pipeline from raw data → trained model → evaluation → FastAPI → dashboard.

---

## Week 2 output checklist

### AI / ML

| Deliverable | Status | Location |
|-------------|--------|----------|
| Clean dataset | ✅ | `datasets/processed/student_performance_cleaned.csv` |
| EDA completed | ✅ | `datasets/processed/eda/`, `notebooks/03_eda_ai_insights.ipynb` |
| Features engineered | ✅ | `datasets/final/`, Day 4 script |
| ML model trained | ✅ | Random Forest + XGBoost, `ml-models/saved_models/` |
| Evaluation metrics | ✅ | `ml-models/evaluation/` |

### Backend

| Deliverable | Status | Location |
|-------------|--------|----------|
| Prediction API | ✅ | `POST /api/predict`, `POST /predict` |

### Frontend

| Deliverable | Status | Location |
|-------------|--------|----------|
| Prediction form | ✅ | `MLPredictPanel` on dashboard |
| Result visualization | ✅ | Prediction label, confidence %, recommendation |

---

## ML pipeline layout

```
ml-models/
├── training/          # Training scripts & logs
│   ├── README.md
│   └── logs/
│       └── training_log_v1.json
├── evaluation/        # Metrics, confusion matrix, AI Analyzer
├── inference/         # API inference (see backend/app/ml/)
└── saved_models/      # Versioned artifacts
    ├── model_manifest.json
    ├── performance_model_v1.joblib
    └── pass_fail_model_v1.joblib
```

---

## Student Risk Detection (recruiter feature)

The API returns:

| Signal | Meaning |
|--------|---------|
| `high_risk` | Model flags at-risk / fail probability |
| `low_performance_chance` | % chance of scoring below 60% |
| `burnout_probability` | % from low sleep + high study load |

---

## What you learned (Week 2)

1. **Pandas** — clean, merge, transform (Days 1–2)
2. **EDA** — correlation, distributions, trends (Day 3)
3. **Feature engineering** — custom scores, importance (Day 4)
4. **ML training** — Random Forest, XGBoost, `train_test_split` (Day 5)
5. **Evaluation** — accuracy, precision, recall, F1, confusion matrix (Day 6)
6. **FastAPI inference** — frontend → API → model (Day 7)

---

## Priority order (completed)

1. Dataset cleaning ✅  
2. EDA ✅  
3. Feature engineering ✅  
4. Random Forest model ✅  
5. API integration ✅  

---

## Day-by-day docs

| Day | Topic | Doc |
|-----|-------|-----|
| 1 | Dataset collection | [dataset-research-day1.md](dataset-research-day1.md) |
| 2 | Data cleaning | [dataset-cleaning-day2.md](dataset-cleaning-day2.md) |
| 3 | EDA | [dataset-eda-day3.md](dataset-eda-day3.md) |
| 4 | Feature engineering | [dataset-feature-engineering-day4.md](dataset-feature-engineering-day4.md) |
| 5 | Train models | [dataset-train-day5.md](dataset-train-day5.md) |
| 6 | Evaluation | [dataset-evaluate-day6.md](dataset-evaluate-day6.md) |
| 7 | ML API | [day7-ml-api.md](day7-ml-api.md) |

---

## Run full pipeline

```bash
python datasets/scripts/download_datasets.py
python datasets/scripts/clean_data.py
python datasets/scripts/eda_analysis.py
python datasets/scripts/feature_engineering.py
python datasets/scripts/train_models.py
python datasets/scripts/evaluate_models.py
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

---

## Optional next (Week 3+)

- MLflow / Weights & Biases experiment tracking
- Retrain with grade features for higher R²
- TensorBoard (if moving to neural nets later)

**Advice:** Master this pipeline before transformers or deep learning — that is what companies value.
