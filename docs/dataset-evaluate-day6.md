# Day 6 — Model Evaluation

**Goal:** Proper ML evaluation — metrics, visualizations, and recruiter-ready AI insights.

---

## Classification metrics (pass / fail)

| Metric | Meaning |
|--------|---------|
| **Accuracy** | Overall correct predictions |
| **Precision** | Of predicted at-risk, how many truly are |
| **Recall** | Of actual at-risk, how many we catch |
| **F1-score** | Balance of precision and recall |

---

## Visualizations

| Chart | File |
|-------|------|
| Confusion matrix | `ml-models/evaluation/confusion_matrix_*.png` |
| Feature importance | `ml-models/evaluation/feature_importance_*.png` |

---

## AI Performance Analyzer

Auto-generated insights, e.g.:

> Attendance is the strongest factor affecting student success.

Outputs:
- `ml-models/evaluation/ai_performance_analyzer.md`
- `ml-models/evaluation/ai_performance_analyzer.json`

---

## Commands

```bash
python datasets/scripts/train_models.py      # prerequisite
python datasets/scripts/evaluate_models.py
jupyter notebook notebooks/06_model_evaluation.ipynb
```

---

## Checklist

- [x] Accuracy, precision, recall, F1
- [x] Confusion matrix
- [x] Feature importance graph
- [x] AI Performance Analyzer report
