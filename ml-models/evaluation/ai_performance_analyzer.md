# AI Performance Analyzer

**MentorMind AI** — Day 6 Model Evaluation

*Generated: 2026-05-25T10:19:43.250772+00:00*

---

## Executive summary

Wellness (sleep proxy) is the strongest factor affecting student success (23.8% of model importance for pass/fail prediction).

## Classification metrics (pass / fail)

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|-----|
| Random Forest | 62.2% | 66.7% | 58.9% | 0.63 |
| Xgboost | 58.4% | 62.6% | 55.4% | 0.59 |

## AI insights

1. Wellness (sleep proxy) is the strongest factor affecting student success (23.8% of model importance for pass/fail prediction).

2. Attendance most strongly drives performance score predictions.

3. At-risk detection: 62.2% accuracy, 66.7% precision, 58.9% recall, F1 0.63.

4. Recall is below 70% — the model misses some at-risk students. Collect more failure cases or tune threshold to improve early intervention.

## Visualizations

| Chart | File |
|-------|------|
| Confusion matrix (RF) | `confusion_matrix_random_forest.png` |
| Feature importance (RF) | `feature_importance_random_forest.png` |
