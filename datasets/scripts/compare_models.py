#!/usr/bin/env python3
"""
Week 3 Day 1 — Train & compare ML models.

Models: Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost.
Outputs: results/metrics/, results/graphs/, results/reports/

Usage:
  python datasets/scripts/compare_models.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS = REPO_ROOT / "results"
METRICS_DIR = RESULTS / "metrics"
GRAPHS_DIR = RESULTS / "graphs"
REPORTS_DIR = RESULTS / "reports"
ML_MODELS = REPO_ROOT / "ml-models"
SAVED = ML_MODELS / "saved_models"
MODEL_VERSION = "v2"

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
    "assignment_completion_score": "Assignments",
    "exam_readiness_score": "Exam readiness",
    "productivity_index": "Productivity",
    "consistency_score": "Consistency",
    "wellness_score": "Wellness",
}


def _get_model_registry():
    """Return list of (name, reg_ctor, clf_ctor) — None ctor = skip."""
    registry = [
        (
            "random_forest",
            lambda: RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
            lambda: RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
        ),
        (
            "gradient_boosting",
            lambda: GradientBoostingRegressor(n_estimators=150, max_depth=5, random_state=42),
            lambda: GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42),
        ),
    ]
    try:
        from xgboost import XGBClassifier, XGBRegressor

        registry.append(
            (
                "xgboost",
                lambda: XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.08, random_state=42, n_jobs=-1),
                lambda: XGBClassifier(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.08,
                    random_state=42,
                    n_jobs=-1,
                    eval_metric="logloss",
                ),
            )
        )
    except Exception as e:
        print(f"[SKIP] xgboost: {e}")

    try:
        from lightgbm import LGBMClassifier, LGBMRegressor

        registry.append(
            (
                "lightgbm",
                lambda: LGBMRegressor(n_estimators=200, max_depth=6, learning_rate=0.08, random_state=42, verbose=-1),
                lambda: LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.08, random_state=42, verbose=-1),
            )
        )
    except ImportError:
        print("[SKIP] lightgbm — pip install lightgbm")

    try:
        from catboost import CatBoostClassifier, CatBoostRegressor

        registry.append(
            (
                "catboost",
                lambda: CatBoostRegressor(iterations=200, depth=6, learning_rate=0.08, random_seed=42, verbose=0),
                lambda: CatBoostClassifier(iterations=200, depth=6, learning_rate=0.08, random_seed=42, verbose=0),
            )
        )
    except ImportError:
        print("[SKIP] catboost — pip install catboost")

    return registry


def _importance_dict(model, features: list[str]) -> dict[str, float]:
    if not hasattr(model, "feature_importances_"):
        return {}
    imp = model.feature_importances_
    total = imp.sum() or 1
    return {
        features[i]: round(float(imp[i] / total * 100), 2)
        for i in range(len(features))
    }


def _train_one(name: str, reg_ctor, clf_ctor, X_train, X_test, ys_train, ys_test, yp_train, yp_test):
    t0 = time.perf_counter()
    reg = reg_ctor()
    reg.fit(X_train, ys_train)
    reg_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    clf = clf_ctor()
    clf.fit(X_train, yp_train)
    clf_time = time.perf_counter() - t1

    ys_pred = reg.predict(X_test)
    yp_pred = clf.predict(X_test)

    return {
        "model": name,
        "train_time_regression_sec": round(reg_time, 3),
        "train_time_classification_sec": round(clf_time, 3),
        "train_time_total_sec": round(reg_time + clf_time, 3),
        "regression": {
            "mae": round(float(mean_absolute_error(ys_test, ys_pred)), 3),
            "r2": round(float(r2_score(ys_test, ys_pred)), 4),
        },
        "classification": {
            "accuracy": round(float(accuracy_score(yp_test, yp_pred)), 4),
            "precision": round(float(precision_score(yp_test, yp_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(yp_test, yp_pred, zero_division=0)), 4),
            "f1_score": round(float(f1_score(yp_test, yp_pred, zero_division=0)), 4),
        },
        "feature_importance_classification": _importance_dict(clf, list(X_train.columns)),
        "feature_importance_regression": _importance_dict(reg, list(X_train.columns)),
        "regressor": reg,
        "classifier": clf,
    }


def _plot_comparisons(df: pd.DataFrame, best_name: str) -> None:
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    colors = ["#8b5cf6" if m == best_name else "#64748b" for m in df["model"]]

    axes[0].barh(df["model"], df["accuracy"] * 100, color=colors)
    axes[0].set_xlabel("Accuracy %")
    axes[0].set_title("Classification Accuracy")
    axes[0].invert_yaxis()

    axes[1].barh(df["model"], df["f1_score"], color=colors)
    axes[1].set_xlabel("F1")
    axes[1].set_title("F1 Score")

    axes[2].barh(df["model"], df["train_time_total_sec"], color=colors)
    axes[2].set_xlabel("Seconds")
    axes[2].set_title("Training Speed (total)")

    fig.suptitle("Week 3 Day 1 — Model Comparison", y=1.02)
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "model_comparison_overview.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    # R² comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(df["model"], df["r2"], color=colors)
    ax.set_xlabel("R² (regression)")
    ax.set_title("Performance Score Prediction (R²)")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "model_comparison_r2.png", dpi=120)
    plt.close(fig)


def _plot_best_importance(best: dict) -> None:
    imp = best.get("feature_importance_classification") or best.get("feature_importance_regression") or {}
    if not imp:
        return
    sorted_imp = sorted(imp.items(), key=lambda x: x[1])
    labels = [FEATURE_LABELS.get(k, k) for k, _ in sorted_imp]
    values = [v for _, v in sorted_imp]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(labels, values, color="#8b5cf6")
    ax.set_xlabel("Importance %")
    ax.set_title(f"Feature Importance — {best['model'].replace('_', ' ').title()} (best F1)")
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "feature_importance_best.png", dpi=120)
    plt.close(fig)


def _write_report(comparison: dict, best: dict) -> None:
    lines = [
        "# Week 3 Day 1 — Model Comparison Report",
        "",
        f"*Generated: {comparison['generated_at']}*",
        "",
        "## Best model (classification F1)",
        "",
        f"**{best['model'].replace('_', ' ').title()}** — F1 {best['classification']['f1_score']}, "
        f"Accuracy {best['classification']['accuracy']*100:.1f}%, "
        f"Train time {best['train_time_total_sec']}s",
        "",
        "## Comparison table",
        "",
        "| Model | Accuracy | Precision | Recall | F1 | R² | Train (s) |",
        "|-------|----------|-----------|--------|-----|-----|-----------|",
    ]
    for r in comparison["results"]:
        c = r["classification"]
        reg = r["regression"]
        lines.append(
            f"| {r['model']} | {c['accuracy']*100:.1f}% | {c['precision']*100:.1f}% | "
            f"{c['recall']*100:.1f}% | {c['f1_score']:.2f} | {reg['r2']:.3f} | {r['train_time_total_sec']} |"
        )
    lines.extend(
        [
            "",
            "## Top features (best model)",
            "",
        ]
    )
    imp = best.get("feature_importance_classification", {})
    for feat, pct in sorted(imp.items(), key=lambda x: -x[1])[:5]:
        label = FEATURE_LABELS.get(feat, feat)
        lines.append(f"- **{label}**: {pct}%")

    lines.extend(
        [
            "",
            "## Graphs",
            "",
            "- `results/graphs/model_comparison_overview.png`",
            "- `results/graphs/model_comparison_r2.png`",
            "- `results/graphs/feature_importance_best.png`",
            "",
            "## Saved artifact",
            "",
            f"`ml-models/saved_models/performance_model_{MODEL_VERSION}.joblib`",
            "",
        ]
    )
    (REPORTS_DIR / "model_comparison_report.md").write_text("\n".join(lines))


def _save_best_model(best: dict) -> None:
    SAVED.mkdir(parents=True, exist_ok=True)
    bundle_reg = {
        "model": best["regressor"],
        "features": API_FEATURE_COLUMNS,
        "task": "regression",
        "algorithm": best["model"],
    }
    bundle_clf = {
        "model": best["classifier"],
        "features": API_FEATURE_COLUMNS,
        "task": "classification",
        "algorithm": best["model"],
    }
    reg_path = SAVED / f"performance_model_{MODEL_VERSION}.joblib"
    clf_path = SAVED / f"pass_fail_model_{MODEL_VERSION}.joblib"
    joblib.dump(bundle_reg, reg_path)
    joblib.dump(bundle_clf, clf_path)

    manifest = {
        "version": MODEL_VERSION,
        "performance_model": reg_path.name,
        "pass_fail_model": clf_path.name,
        "score_algorithm": best["model"],
        "pass_algorithm": best["model"],
        "selected_by": "classification_f1",
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    (SAVED / "model_manifest.json").write_text(json.dumps(manifest, indent=2))
    (ML_MODELS / "best_model.json").write_text(
        json.dumps(
            {
                "score_model": best["model"],
                "score_file": f"saved_models/{reg_path.name}",
                "pass_model": best["model"],
                "pass_file": f"saved_models/{clf_path.name}",
                "version": MODEL_VERSION,
            },
            indent=2,
        )
    )
    print(f"[OK] Best model saved: {reg_path.name}, {clf_path.name}")


def compare_models(test_size: float = 0.2, random_state: int = 42) -> dict:
    print("=== Week 3 Day 1: Model Comparison ===\n")

    for d in (METRICS_DIR, GRAPHS_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(REPO_ROOT / "datasets/processed/student_performance_cleaned.csv")
    df = add_api_features(df)
    X = features_dataframe(df)
    y_score = df[TARGET_SCORE]
    y_pass = df[TARGET_PASS]

    X_train, X_test, ys_train, ys_test = train_test_split(X, y_score, test_size=test_size, random_state=random_state)
    _, _, yp_train, yp_test = train_test_split(X, y_pass, test_size=test_size, random_state=random_state)

    registry = _get_model_registry()
    print(f"Training {len(registry)} model families on {len(X_train)} rows...\n")

    results = []
    best_row = None
    best_objs = None
    for name, reg_ctor, clf_ctor in registry:
        print(f"  Training {name}...")
        row = _train_one(name, reg_ctor, clf_ctor, X_train, X_test, ys_train, ys_test, yp_train, yp_test)
        serial = {k: v for k, v in row.items() if k not in ("regressor", "classifier")}
        results.append(serial)
        c = row["classification"]
        print(f"    F1={c['f1_score']:.3f} acc={c['accuracy']:.3f} R²={row['regression']['r2']:.3f} time={row['train_time_total_sec']}s")
        if best_row is None or c["f1_score"] > best_row["classification"]["f1_score"]:
            best_row = serial
            best_objs = row

    comparison = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "models_trained": len(results),
        "selection_criteria": "highest_classification_f1",
        "best_model": best_row["model"],
        "results": results,
        "best": best_row,
    }

    (METRICS_DIR / "model_comparison.json").write_text(json.dumps(comparison, indent=2))

    # DataFrame for plots
    plot_df = pd.DataFrame(
        [
            {
                "model": r["model"],
                "accuracy": r["classification"]["accuracy"],
                "f1_score": r["classification"]["f1_score"],
                "r2": r["regression"]["r2"],
                "train_time_total_sec": r["train_time_total_sec"],
            }
            for r in results
        ]
    )
    _plot_comparisons(plot_df, best_row["model"])
    _plot_best_importance(best_row)
    _write_report(comparison, best_row)
    _save_best_model(best_objs)

    print(f"\n[OK] Metrics: {METRICS_DIR / 'model_comparison.json'}")
    print(f"[OK] Report: {REPORTS_DIR / 'model_comparison_report.md'}")
    print(f"\n--- Winner: {best_row['model']} (F1={best_row['classification']['f1_score']}) ---")

    return comparison


def main() -> int:
    try:
        compare_models()
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
