#!/usr/bin/env python3
"""
Day 6 — Model evaluation + AI Performance Analyzer.

Metrics: accuracy, precision, recall, F1.
Plots: confusion matrix, feature importance.
Report: recruiter-ready AI insights.

Usage:
  python datasets/scripts/evaluate_models.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
ML_MODELS = REPO_ROOT / "ml-models"
EVAL_DIR = ML_MODELS / "evaluation"
PROCESSED = REPO_ROOT / "datasets" / "processed"
CLEANED_CSV = PROCESSED / "student_performance_cleaned.csv"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ml_features import (  # noqa: E402
    API_FEATURE_COLUMNS,
    TARGET_PASS,
    TARGET_SCORE,
    add_api_features,
    features_dataframe,
)

FEATURE_LABELS = {
    "study_hours": "Study hours",
    "attendance_pct": "Attendance",
    "past_failures": "Past failures",
    "assignment_completion_score": "Assignment completion",
    "exam_readiness_score": "Exam readiness",
    "productivity_index": "Productivity index",
    "consistency_score": "Consistency score",
    "wellness_score": "Wellness (sleep proxy)",
}

MODEL_BUNDLES = [
    ("random_forest", "pass_fail_random_forest.joblib", "performance_random_forest.joblib"),
    ("xgboost", "pass_fail_xgboost.joblib", "performance_xgboost.joblib"),
]


def _load_test_split(test_size=0.2, random_state=42):
    df = pd.read_csv(CLEANED_CSV)
    df = add_api_features(df)
    X = features_dataframe(df)
    y_pass = df[TARGET_PASS]
    y_score = df[TARGET_SCORE]
    _, X_test, _, yp_test = train_test_split(
        X, y_pass, test_size=test_size, random_state=random_state
    )
    _, _, _, ys_test = train_test_split(
        X, y_score, test_size=test_size, random_state=random_state
    )
    return X_test, yp_test, ys_test


def _classification_metrics(y_true, y_pred) -> dict:
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
    }


def plot_confusion_matrix(y_true, y_pred, title: str, out: Path) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Purples",
        xticklabels=["Pass (0)", "At-risk (1)"],
        yticklabels=["Pass (0)", "At-risk (1)"],
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_feature_importance(model, features: list[str], title: str, out: Path) -> None:
    if not hasattr(model, "feature_importances_"):
        return
    imp = pd.Series(model.feature_importances_, index=features).sort_values(ascending=True)
    labels = [FEATURE_LABELS.get(f, f) for f in imp.index]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(labels, imp.values, color="#8b5cf6")
    ax.set_xlabel("Importance")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return imp


def generate_ai_insights(
    model_name: str,
    clf_metrics: dict,
    reg_importance: pd.Series | None,
    clf_importance: pd.Series | None,
) -> list[dict]:
    insights = []

    top_clf = None
    if clf_importance is not None and len(clf_importance):
        top_feat = clf_importance.idxmax()
        top_label = FEATURE_LABELS.get(top_feat, top_feat)
        top_clf = top_feat
        pct = round(float(clf_importance.max() / clf_importance.sum() * 100), 1)
        insights.append(
            {
                "type": "strongest_factor",
                "insight": (
                    f"**{top_label}** is the strongest factor affecting student success "
                    f"({pct}% of model importance for pass/fail prediction)."
                ),
                "feature": top_feat,
                "importance_pct": pct,
            }
        )

    if reg_importance is not None and len(reg_importance):
        top_reg = reg_importance.idxmax()
        top_reg_label = FEATURE_LABELS.get(top_reg, top_reg)
        if top_reg != top_clf:
            insights.append(
                {
                    "type": "score_driver",
                    "insight": (
                        f"**{top_reg_label}** most strongly drives performance score predictions."
                    ),
                    "feature": top_reg,
                }
            )

    insights.append(
        {
            "type": "classification_performance",
            "insight": (
                f"At-risk detection: **{clf_metrics['accuracy']*100:.1f}% accuracy**, "
                f"**{clf_metrics['precision']*100:.1f}% precision**, "
                f"**{clf_metrics['recall']*100:.1f}% recall**, "
                f"F1 **{clf_metrics['f1_score']:.2f}**."
            ),
            "metrics": clf_metrics,
        }
    )

    if clf_metrics["recall"] < 0.7:
        insights.append(
            {
                "type": "recommendation",
                "insight": (
                    "Recall is below 70% — the model misses some at-risk students. "
                    "Collect more failure cases or tune threshold to improve early intervention."
                ),
            }
        )

    if clf_metrics["precision"] > 0.6 and clf_metrics["recall"] > 0.6:
        insights.append(
            {
                "type": "recommendation",
                "insight": (
                    "Balanced precision and recall — suitable for MVP coaching alerts "
                    "on the MentorMind dashboard."
                ),
            }
        )

    # Actionable coaching from top feature
    if top_clf == "attendance_pct":
        insights.append(
            {
                "type": "coaching",
                "insight": (
                    "Prioritize attendance interventions: students below 90% attendance "
                    "show measurably lower pass rates in the dataset."
                ),
            }
        )
    elif top_clf == "study_hours":
        insights.append(
            {
                "type": "coaching",
                "insight": (
                    "Study time is the top success lever — recommend structured weekly "
                    "study blocks in the AI study planner."
                ),
            }
        )
    elif top_clf == "exam_readiness_score":
        insights.append(
            {
                "type": "coaching",
                "insight": (
                    "Exam readiness composite (study + attendance + assignments) is the best "
                    "predictor — surface this score prominently on the dashboard."
                ),
            }
        )

    return insights


def write_analyzer_report(all_results: dict, all_insights: list[dict]) -> None:
    lines = [
        "# AI Performance Analyzer",
        "",
        "**MentorMind AI** — Day 6 Model Evaluation",
        "",
        f"*Generated: {datetime.now(timezone.utc).isoformat()}*",
        "",
        "---",
        "",
        "## Executive summary",
        "",
    ]
    best = all_results.get("random_forest") or next(iter(all_results.values()))
    top_insight = next((i for i in all_insights if i["type"] == "strongest_factor"), None)
    if top_insight:
        lines.append(top_insight["insight"].replace("**", ""))
        lines.append("")

    lines.extend(["## Classification metrics (pass / fail)", ""])
    lines.append("| Model | Accuracy | Precision | Recall | F1 |")
    lines.append("|-------|----------|-----------|--------|-----|")
    for name, res in all_results.items():
        m = res["classification"]
        lines.append(
            f"| {name.replace('_', ' ').title()} | {m['accuracy']*100:.1f}% | "
            f"{m['precision']*100:.1f}% | {m['recall']*100:.1f}% | {m['f1_score']:.2f} |"
        )

    lines.extend(["", "## AI insights", ""])
    for i, ins in enumerate(all_insights, 1):
        lines.append(f"{i}. {ins['insight'].replace('**', '')}")
        lines.append("")

    lines.extend(
        [
            "## Visualizations",
            "",
            "| Chart | File |",
            "|-------|------|",
            "| Confusion matrix (RF) | `confusion_matrix_random_forest.png` |",
            "| Feature importance (RF) | `feature_importance_random_forest.png` |",
            "",
        ]
    )
    (EVAL_DIR / "ai_performance_analyzer.md").write_text("\n".join(lines))


def evaluate_models() -> dict:
    print("=== Day 6: Model Evaluation ===\n")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    if not CLEANED_CSV.exists():
        raise FileNotFoundError("Run clean_data.py and train_models.py first.")

    X_test, y_pass_test, _ = _load_test_split()
    all_results = {}
    all_insights: list[dict] = []

    sns.set_theme(style="whitegrid")

    for model_name, pass_file, score_file in MODEL_BUNDLES:
        pass_path = ML_MODELS / pass_file
        score_path = ML_MODELS / score_file
        if not pass_path.exists():
            print(f"[SKIP] {model_name} — {pass_file} not found")
            continue

        pass_bundle = joblib.load(pass_path)
        clf = pass_bundle["model"]
        features = pass_bundle["features"]
        y_pred = clf.predict(X_test[features])

        metrics = _classification_metrics(y_pass_test, y_pred)
        report = classification_report(
            y_pass_test, y_pred, zero_division=0, output_dict=True
        )

        plot_confusion_matrix(
            y_pass_test,
            y_pred,
            f"Confusion Matrix — {model_name.replace('_', ' ').title()}",
            EVAL_DIR / f"confusion_matrix_{model_name}.png",
        )
        clf_imp = plot_feature_importance(
            clf,
            features,
            f"Feature Importance (Pass/Fail) — {model_name.replace('_', ' ').title()}",
            EVAL_DIR / f"feature_importance_{model_name}.png",
        )

        reg_imp = None
        if score_path.exists():
            reg_bundle = joblib.load(score_path)
            reg = reg_bundle["model"]
            reg_imp = plot_feature_importance(
                reg,
                features,
                f"Feature Importance (Score) — {model_name.replace('_', ' ').title()}",
                EVAL_DIR / f"feature_importance_score_{model_name}.png",
            )

        all_results[model_name] = {
            "classification": metrics,
            "classification_report": report,
        }
        insights = generate_ai_insights(model_name, metrics, reg_imp, clf_imp)
        if model_name == "random_forest":
            all_insights = insights

        print(f"[{model_name.upper()}] acc={metrics['accuracy']:.2%} "
              f"prec={metrics['precision']:.2%} rec={metrics['recall']:.2%} "
              f"F1={metrics['f1_score']:.2f}")

    evaluation = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "test_rows": len(X_test),
        "models": all_results,
        "ai_insights": all_insights,
    }

    (EVAL_DIR / "evaluation_metrics.json").write_text(json.dumps(evaluation, indent=2))
    (EVAL_DIR / "ai_performance_analyzer.json").write_text(
        json.dumps({"insights": all_insights, "models": all_results}, indent=2)
    )
    write_analyzer_report(all_results, all_insights)

    print(f"\n[OK] Metrics: {EVAL_DIR / 'evaluation_metrics.json'}")
    print(f"[OK] AI Analyzer: {EVAL_DIR / 'ai_performance_analyzer.md'}")
    print("\n--- Top insight ---")
    if all_insights:
        print(f"  {all_insights[0]['insight'].replace('**', '')}")

    return evaluation


def main() -> int:
    try:
        evaluate_models()
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
