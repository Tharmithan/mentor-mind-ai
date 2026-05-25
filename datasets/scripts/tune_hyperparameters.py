#!/usr/bin/env python3
"""
Week 3 Day 2 — Hyperparameter tuning (XGBoost).

Uses GridSearchCV and RandomizedSearchCV on n_estimators, max_depth, learning_rate.
Compares baseline vs tuned metrics and writes Model Training Report.

Usage:
  python datasets/scripts/tune_hyperparameters.py
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
from scipy.stats import randint, uniform
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS = REPO_ROOT / "results"
METRICS_DIR = RESULTS / "metrics"
GRAPHS_DIR = RESULTS / "graphs"
REPORTS_DIR = RESULTS / "reports"
ML_MODELS = REPO_ROOT / "ml-models"
SAVED = ML_MODELS / "saved_models"
TUNED_VERSION = "v3"

BASELINE_PARAMS = {
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.08,
}

GRID_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.05, 0.08, 0.1],
}

RANDOM_PARAM_DIST = {
    "n_estimators": randint(80, 350),
    "max_depth": randint(3, 10),
    "learning_rate": uniform(0.03, 0.12),
    "subsample": uniform(0.75, 0.2),
    "colsample_bytree": uniform(0.75, 0.2),
}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ml_features import (  # noqa: E402
    API_FEATURE_COLUMNS,
    TARGET_PASS,
    TARGET_SCORE,
    add_api_features,
    features_dataframe,
)


def _classification_metrics(y_true, y_pred) -> dict:
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
    }


def _regression_metrics(y_true, y_pred) -> dict:
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def _evaluate_pair(reg, clf, X_test, ys_test, yp_test) -> dict:
    ys_pred = reg.predict(X_test)
    yp_pred = clf.predict(X_test)
    return {
        "regression": _regression_metrics(ys_test, ys_pred),
        "classification": _classification_metrics(yp_test, yp_pred),
    }


def _train_baseline(X_train, X_test, ys_train, ys_test, yp_train, yp_test, random_state: int):
    from xgboost import XGBClassifier, XGBRegressor

    t0 = time.perf_counter()
    reg = XGBRegressor(**BASELINE_PARAMS, random_state=random_state, n_jobs=-1)
    reg.fit(X_train, ys_train)
    clf = XGBClassifier(
        **BASELINE_PARAMS,
        random_state=random_state,
        n_jobs=-1,
        eval_metric="logloss",
    )
    clf.fit(X_train, yp_train)
    train_time = round(time.perf_counter() - t0, 3)
    metrics = _evaluate_pair(reg, clf, X_test, ys_test, yp_test)
    return {
        "label": "baseline",
        "params": BASELINE_PARAMS.copy(),
        "train_time_sec": train_time,
        "metrics": metrics,
        "regressor": reg,
        "classifier": clf,
    }


def _run_grid_search(X_train, yp_train, random_state: int) -> dict:
    from xgboost import XGBClassifier

    base = XGBClassifier(random_state=random_state, n_jobs=-1, eval_metric="logloss")
    t0 = time.perf_counter()
    search = GridSearchCV(
        base,
        GRID_PARAM_GRID,
        scoring="f1",
        cv=3,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_train, yp_train)
    elapsed = round(time.perf_counter() - t0, 3)
    return {
        "method": "GridSearchCV",
        "best_params": {k: int(v) if k != "learning_rate" else round(float(v), 4) for k, v in search.best_params_.items()},
        "best_cv_f1": round(float(search.best_score_), 4),
        "cv_folds": 3,
        "combinations_tested": len(search.cv_results_["params"]),
        "search_time_sec": elapsed,
        "estimator": search.best_estimator_,
    }


def _run_random_search(X_train, yp_train, random_state: int, n_iter: int = 24) -> dict:
    from xgboost import XGBClassifier

    base = XGBClassifier(random_state=random_state, n_jobs=-1, eval_metric="logloss")
    t0 = time.perf_counter()
    search = RandomizedSearchCV(
        base,
        RANDOM_PARAM_DIST,
        n_iter=n_iter,
        scoring="f1",
        cv=3,
        n_jobs=-1,
        random_state=random_state,
        verbose=0,
    )
    search.fit(X_train, yp_train)
    elapsed = round(time.perf_counter() - t0, 3)
    best = search.best_params_
    cleaned = {}
    for k, v in best.items():
        if k in ("n_estimators", "max_depth"):
            cleaned[k] = int(v)
        else:
            cleaned[k] = round(float(v), 4)
    return {
        "method": "RandomizedSearchCV",
        "best_params": cleaned,
        "best_cv_f1": round(float(search.best_score_), 4),
        "cv_folds": 3,
        "iterations": n_iter,
        "search_time_sec": elapsed,
        "estimator": search.best_estimator_,
    }


def _train_tuned_from_params(
    params: dict,
    X_train,
    X_test,
    ys_train,
    ys_test,
    yp_train,
    yp_test,
    random_state: int,
    label: str,
):
    from xgboost import XGBClassifier, XGBRegressor

    core = {k: v for k, v in params.items() if k in ("n_estimators", "max_depth", "learning_rate")}
    t0 = time.perf_counter()
    reg = XGBRegressor(**core, random_state=random_state, n_jobs=-1)
    reg.fit(X_train, ys_train)
    clf = XGBClassifier(**params, random_state=random_state, n_jobs=-1, eval_metric="logloss")
    clf.fit(X_train, yp_train)
    train_time = round(time.perf_counter() - t0, 3)
    metrics = _evaluate_pair(reg, clf, X_test, ys_test, yp_test)
    return {
        "label": label,
        "params": params,
        "train_time_sec": train_time,
        "metrics": metrics,
        "regressor": reg,
        "classifier": clf,
    }


def _delta(before: float, after: float) -> dict:
    diff = after - before
    pct = (diff / before * 100) if before else 0.0
    return {"before": before, "after": after, "delta": round(diff, 4), "delta_pct": round(pct, 2)}


def _plot_before_after(baseline: dict, tuned: dict) -> None:
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    labels = ["Baseline", "Grid tuned", "Random tuned", "Best tuned"]
    stages = [
        baseline["metrics"]["classification"],
        tuned.get("grid_test", baseline["metrics"])["classification"] if "grid_test" in tuned else baseline["metrics"]["classification"],
    ]
    # Use explicit list from report data passed via tuned dict
    acc = [
        baseline["metrics"]["classification"]["accuracy"] * 100,
        tuned["grid"]["metrics"]["classification"]["accuracy"] * 100,
        tuned["random"]["metrics"]["classification"]["accuracy"] * 100,
        tuned["best"]["metrics"]["classification"]["accuracy"] * 100,
    ]
    f1 = [
        baseline["metrics"]["classification"]["f1_score"],
        tuned["grid"]["metrics"]["classification"]["f1_score"],
        tuned["random"]["metrics"]["classification"]["f1_score"],
        tuned["best"]["metrics"]["classification"]["f1_score"],
    ]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    x = np.arange(len(labels))
    colors = ["#64748b", "#94a3b8", "#94a3b8", "#8b5cf6"]
    axes[0].bar(x, acc, color=colors)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=15, ha="right")
    axes[0].set_ylabel("Accuracy %")
    axes[0].set_title("XGBoost — Accuracy")

    axes[1].bar(x, f1, color=colors)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=15, ha="right")
    axes[1].set_ylabel("F1")
    axes[1].set_title("XGBoost — F1 Score")

    fig.suptitle("Week 3 Day 2 — Before vs After Tuning", y=1.02)
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "tuning_before_after.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def _write_training_report(payload: dict) -> None:
    b = payload["baseline"]
    g = payload["grid_tuned"]
    r = payload["random_tuned"]
    best = payload["best_tuned"]
    imp = payload["improvements"]

    lines = [
        "# Model Training Report",
        "",
        "**Week 3 Day 2 — XGBoost Hyperparameter Tuning**",
        "",
        f"*Generated: {payload['generated_at']}*",
        "",
        "## Executive summary",
        "",
        f"Tuned XGBoost with **{best['selected_from']}** search. "
        f"Test F1 improved from **{b['metrics']['classification']['f1_score']:.3f}** "
        f"to **{best['metrics']['classification']['f1_score']:.3f}** "
        f"({imp['f1_score']['delta_pct']:+.1f}%). "
        f"Accuracy: **{b['metrics']['classification']['accuracy']*100:.1f}%** → "
        f"**{best['metrics']['classification']['accuracy']*100:.1f}%** "
        f"({imp['accuracy']['delta_pct']:+.1f}%).",
        "",
        "## Best parameters",
        "",
        "```json",
        json.dumps(best["params"], indent=2),
        "```",
        "",
        "| Parameter | Baseline | Best tuned |",
        "|-----------|----------|------------|",
    ]
    for key in ("n_estimators", "max_depth", "learning_rate"):
        lines.append(
            f"| {key} | {b['params'].get(key, '—')} | {best['params'].get(key, '—')} |"
        )
    if "subsample" in best["params"]:
        lines.append(f"| subsample | — | {best['params']['subsample']} |")
    if "colsample_bytree" in best["params"]:
        lines.append(f"| colsample_bytree | — | {best['params']['colsample_bytree']} |")

    lines.extend(
        [
            "",
            "## Search methods",
            "",
            "### GridSearchCV",
            "",
            f"- Param grid: `n_estimators`, `max_depth`, `learning_rate` ({payload['grid_search']['combinations_tested']} combos)",
            f"- Best CV F1: **{payload['grid_search']['best_cv_f1']:.4f}**",
            f"- Search time: **{payload['grid_search']['search_time_sec']}s**",
            f"- Test F1 after refit: **{g['metrics']['classification']['f1_score']:.4f}**",
            "",
            "### RandomizedSearchCV",
            "",
            f"- Iterations: **{payload['random_search']['iterations']}**",
            f"- Best CV F1: **{payload['random_search']['best_cv_f1']:.4f}**",
            f"- Search time: **{payload['random_search']['search_time_sec']}s**",
            f"- Test F1 after refit: **{r['metrics']['classification']['f1_score']:.4f}**",
            "",
            "## Before vs after (test set)",
            "",
            "| Metric | Baseline | Best tuned | Δ |",
            "|--------|----------|------------|---|",
            f"| Accuracy | {imp['accuracy']['before']*100:.1f}% | {imp['accuracy']['after']*100:.1f}% | {imp['accuracy']['delta_pct']:+.2f}% |",
            f"| Precision | {imp['precision']['before']*100:.1f}% | {imp['precision']['after']*100:.1f}% | {imp['precision']['delta_pct']:+.2f}% |",
            f"| Recall | {imp['recall']['before']*100:.1f}% | {imp['recall']['after']*100:.1f}% | {imp['recall']['delta_pct']:+.2f}% |",
            f"| F1 | {imp['f1_score']['before']:.4f} | {imp['f1_score']['after']:.4f} | {imp['f1_score']['delta_pct']:+.2f}% |",
            f"| R² (regression) | {imp['r2']['before']:.4f} | {imp['r2']['after']:.4f} | {imp['r2']['delta_pct']:+.2f}% |",
            "",
            "## Training time",
            "",
            f"| Stage | Seconds |",
            f"|-------|---------|",
            f"| Baseline fit | {b['train_time_sec']} |",
            f"| GridSearchCV | {payload['grid_search']['search_time_sec']} |",
            f"| RandomizedSearchCV | {payload['random_search']['search_time_sec']} |",
            f"| Best tuned refit | {best['train_time_sec']} |",
            f"| **Total pipeline** | **{payload['total_time_sec']}** |",
            "",
            "## Saved artifacts",
            "",
            f"- `results/metrics/hyperparameter_tuning.json`",
            f"- `results/graphs/tuning_before_after.png`",
            f"- `ml-models/saved_models/performance_model_{TUNED_VERSION}.joblib` (if tuned beats baseline)",
            f"- `ml-models/saved_models/pass_fail_model_{TUNED_VERSION}.joblib`",
            "",
            "## Note",
            "",
            "Day 1 winner was Random Forest (F1 ~0.63). This report documents XGBoost tuning; "
            "deploy tuned XGBoost only if it exceeds your production threshold.",
            "",
        ]
    )
    (REPORTS_DIR / "model_training_report.md").write_text("\n".join(lines))


def _save_tuned_models(best_run: dict) -> None:
    SAVED.mkdir(parents=True, exist_ok=True)
    reg_path = SAVED / f"performance_model_{TUNED_VERSION}.joblib"
    clf_path = SAVED / f"pass_fail_model_{TUNED_VERSION}.joblib"
    joblib.dump(
        {"model": best_run["regressor"], "features": API_FEATURE_COLUMNS, "task": "regression", "algorithm": "xgboost_tuned"},
        reg_path,
    )
    joblib.dump(
        {"model": best_run["classifier"], "features": API_FEATURE_COLUMNS, "task": "classification", "algorithm": "xgboost_tuned"},
        clf_path,
    )
    manifest = {
        "version": TUNED_VERSION,
        "performance_model": reg_path.name,
        "pass_fail_model": clf_path.name,
        "algorithm": "xgboost_tuned",
        "params": best_run["params"],
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    (SAVED / f"model_manifest_{TUNED_VERSION}.json").write_text(json.dumps(manifest, indent=2))
    print(f"[OK] Tuned models: {reg_path.name}, {clf_path.name}")


def tune_hyperparameters(test_size: float = 0.2, random_state: int = 42) -> dict:
    print("=== Week 3 Day 2: XGBoost Hyperparameter Tuning ===\n")
    pipeline_start = time.perf_counter()

    for d in (METRICS_DIR, GRAPHS_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    try:
        from xgboost import XGBClassifier  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Install xgboost: pip install xgboost") from exc

    df = pd.read_csv(REPO_ROOT / "datasets/processed/student_performance_cleaned.csv")
    df = add_api_features(df)
    X = features_dataframe(df)
    y_score = df[TARGET_SCORE]
    y_pass = df[TARGET_PASS]

    X_train, X_test, ys_train, ys_test = train_test_split(
        X, y_score, test_size=test_size, random_state=random_state
    )
    _, _, yp_train, yp_test = train_test_split(
        X, y_pass, test_size=test_size, random_state=random_state
    )

    print(f"Train: {len(X_train)} | Test: {len(X_test)}\n")

    print("1/4 Baseline XGBoost...")
    baseline = _train_baseline(X_train, X_test, ys_train, ys_test, yp_train, yp_test, random_state)
    bc = baseline["metrics"]["classification"]
    print(f"     F1={bc['f1_score']:.3f} acc={bc['accuracy']:.3f}\n")

    print("2/4 GridSearchCV (f1, 3-fold CV)...")
    grid_result = _run_grid_search(X_train, yp_train, random_state)
    print(f"     Best CV F1={grid_result['best_cv_f1']:.4f} params={grid_result['best_params']}")
    print(f"     Search time={grid_result['search_time_sec']}s\n")

    grid_tuned = _train_tuned_from_params(
        grid_result["best_params"],
        X_train,
        X_test,
        ys_train,
        ys_test,
        yp_train,
        yp_test,
        random_state,
        "grid_tuned",
    )
    print(
        f"     Test F1={grid_tuned['metrics']['classification']['f1_score']:.3f} "
        f"acc={grid_tuned['metrics']['classification']['accuracy']:.3f}\n"
    )

    print("3/4 RandomizedSearchCV...")
    random_result = _run_random_search(X_train, yp_train, random_state)
    print(f"     Best CV F1={random_result['best_cv_f1']:.4f} params={random_result['best_params']}")
    print(f"     Search time={random_result['search_time_sec']}s\n")

    random_tuned = _train_tuned_from_params(
        random_result["best_params"],
        X_train,
        X_test,
        ys_train,
        ys_test,
        yp_train,
        yp_test,
        random_state,
        "random_tuned",
    )
    print(
        f"     Test F1={random_tuned['metrics']['classification']['f1_score']:.3f} "
        f"acc={random_tuned['metrics']['classification']['accuracy']:.3f}\n"
    )

    candidates = [grid_tuned, random_tuned]
    best_tuned = max(candidates, key=lambda x: x["metrics"]["classification"]["f1_score"])
    best_tuned["selected_from"] = best_tuned["label"]

    improved = best_tuned["metrics"]["classification"]["f1_score"] > bc["f1_score"]
    if improved:
        _save_tuned_models(best_tuned)
    else:
        print("[INFO] Tuned model did not beat baseline on test F1 — v3 artifacts skipped.")

    b_cls = baseline["metrics"]["classification"]
    t_cls = best_tuned["metrics"]["classification"]
    improvements = {
        "accuracy": _delta(b_cls["accuracy"], t_cls["accuracy"]),
        "precision": _delta(b_cls["precision"], t_cls["precision"]),
        "recall": _delta(b_cls["recall"], t_cls["recall"]),
        "f1_score": _delta(b_cls["f1_score"], t_cls["f1_score"]),
        "r2": _delta(
            baseline["metrics"]["regression"]["r2"],
            best_tuned["metrics"]["regression"]["r2"],
        ),
    }

    def _serial(run: dict) -> dict:
        return {
            "label": run["label"],
            "params": run["params"],
            "train_time_sec": run["train_time_sec"],
            "metrics": run["metrics"],
        }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "xgboost",
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "baseline": _serial(baseline),
        "grid_search": {
            "method": grid_result["method"],
            "best_params": grid_result["best_params"],
            "best_cv_f1": grid_result["best_cv_f1"],
            "combinations_tested": grid_result["combinations_tested"],
            "search_time_sec": grid_result["search_time_sec"],
        },
        "random_search": {
            "method": random_result["method"],
            "best_params": random_result["best_params"],
            "best_cv_f1": random_result["best_cv_f1"],
            "iterations": random_result["iterations"],
            "search_time_sec": random_result["search_time_sec"],
        },
        "grid_tuned": _serial(grid_tuned),
        "random_tuned": _serial(random_tuned),
        "best_tuned": _serial(best_tuned) | {"selected_from": best_tuned["selected_from"]},
        "improvements": improvements,
        "beats_baseline": improved,
        "total_time_sec": round(time.perf_counter() - pipeline_start, 2),
    }

    (METRICS_DIR / "hyperparameter_tuning.json").write_text(json.dumps(payload, indent=2))
    _plot_before_after(
        baseline,
        {"grid": grid_tuned, "random": random_tuned, "best": best_tuned},
    )
    _write_training_report(payload)

    print(f"[OK] Metrics: {METRICS_DIR / 'hyperparameter_tuning.json'}")
    print(f"[OK] Report: {REPORTS_DIR / 'model_training_report.md'}")
    print(
        f"\n--- Best: {best_tuned['selected_from']} | "
        f"F1 {bc['f1_score']:.3f} → {t_cls['f1_score']:.3f} "
        f"({improvements['f1_score']['delta_pct']:+.1f}%) ---"
    )
    return payload


def main() -> int:
    try:
        tune_hyperparameters()
        return 0
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
