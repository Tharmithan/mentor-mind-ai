#!/usr/bin/env python3
"""
Day 5 — Train first ML models (Random Forest + XGBoost).

Predicts performance score (regression) and pass/fail (classification).

Usage:
  python datasets/scripts/train_models.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "datasets"
PROCESSED = ROOT / "processed"
FINAL = ROOT / "final"
ML_MODELS = REPO_ROOT / "ml-models"

CLEANED_CSV = PROCESSED / "student_performance_cleaned.csv"
METRICS_JSON = ML_MODELS / "training_metrics.json"
BEST_MODEL_JSON = ML_MODELS / "best_model.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ml_features import (  # noqa: E402
    API_FEATURE_COLUMNS,
    TARGET_PASS,
    TARGET_SCORE,
    add_api_features,
    features_dataframe,
)

RF_SCORE_PATH = ML_MODELS / "performance_random_forest.joblib"
XGB_SCORE_PATH = ML_MODELS / "performance_xgboost.joblib"
RF_PASS_PATH = ML_MODELS / "pass_fail_random_forest.joblib"
XGB_PASS_PATH = ML_MODELS / "pass_fail_xgboost.joblib"


def _load_data() -> pd.DataFrame:
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(f"Run clean_data.py first. Missing {CLEANED_CSV}")
    df = pd.read_csv(CLEANED_CSV)
    return add_api_features(df)


def _eval_regression(y_true, y_pred) -> dict:
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 3),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def _eval_classification(y_true, y_pred) -> dict:
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "report": classification_report(y_true, y_pred, zero_division=0, output_dict=True),
    }


def train_models(test_size: float = 0.2, random_state: int = 42) -> dict:
    print("=== Day 5: Train ML Models ===\n")

    XGBRegressor = None
    XGBClassifier = None
    try:
        from xgboost import XGBClassifier, XGBRegressor
    except ImportError:
        print("[WARN] xgboost not installed — Random Forest only. pip install xgboost")
    except Exception as exc:
        print(f"[WARN] xgboost unavailable ({exc.__class__.__name__}) — Random Forest only.")
        print("       macOS: brew install libomp && pip install xgboost")

    df = _load_data()
    X = features_dataframe(df)
    y_score = df[TARGET_SCORE]
    y_pass = df[TARGET_PASS]

    X_train, X_test, ys_train, ys_test = train_test_split(
        X, y_score, test_size=test_size, random_state=random_state
    )
    _, _, yp_train, yp_test = train_test_split(
        X, y_pass, test_size=test_size, random_state=random_state
    )

    print(f"Train: {len(X_train)} | Test: {len(X_test)} | Features: {len(API_FEATURE_COLUMNS)}\n")

    ML_MODELS.mkdir(parents=True, exist_ok=True)

    # --- Random Forest ---
    rf_reg = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=random_state, n_jobs=-1)
    rf_reg.fit(X_train, ys_train)
    rf_reg_pred = rf_reg.predict(X_test)
    rf_reg_metrics = _eval_regression(ys_test, rf_reg_pred)

    rf_clf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=random_state, n_jobs=-1)
    rf_clf.fit(X_train, yp_train)
    rf_clf_pred = rf_clf.predict(X_test)
    rf_clf_metrics = _eval_classification(yp_test, rf_clf_pred)

    joblib.dump(
        {"model": rf_reg, "features": API_FEATURE_COLUMNS, "task": "regression"},
        RF_SCORE_PATH,
    )
    joblib.dump(
        {"model": rf_clf, "features": API_FEATURE_COLUMNS, "task": "classification"},
        RF_PASS_PATH,
    )
    print(f"[OK] Random Forest score  → {RF_SCORE_PATH.name}  R²={rf_reg_metrics['r2']}")
    print(f"[OK] Random Forest pass   → {RF_PASS_PATH.name}  acc={rf_clf_metrics['accuracy']}")

    xgb_reg_metrics = {"mae": None, "rmse": None, "r2": None, "skipped": True}
    xgb_clf_metrics = {"accuracy": None, "f1": None, "skipped": True}

    if XGBRegressor is not None:
        xgb_reg = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.08,
            random_state=random_state,
            n_jobs=-1,
        )
        xgb_reg.fit(X_train, ys_train)
        xgb_reg_pred = xgb_reg.predict(X_test)
        xgb_reg_metrics = _eval_regression(ys_test, xgb_reg_pred)

        xgb_clf = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.08,
            random_state=random_state,
            n_jobs=-1,
            eval_metric="logloss",
        )
        xgb_clf.fit(X_train, yp_train)
        xgb_clf_pred = xgb_clf.predict(X_test)
        xgb_clf_metrics = _eval_classification(yp_test, xgb_clf_pred)

        joblib.dump(
            {"model": xgb_reg, "features": API_FEATURE_COLUMNS, "task": "regression"},
            XGB_SCORE_PATH,
        )
        joblib.dump(
            {"model": xgb_clf, "features": API_FEATURE_COLUMNS, "task": "classification"},
            XGB_PASS_PATH,
        )
        print(f"[OK] XGBoost score        → {XGB_SCORE_PATH.name}  R²={xgb_reg_metrics['r2']}")
        print(f"[OK] XGBoost pass         → {XGB_PASS_PATH.name}  acc={xgb_clf_metrics['accuracy']}")

    # Pick best by R² (score) and F1 (pass)
    best_score = ("random_forest", rf_reg_metrics)
    best_pass = ("random_forest", rf_clf_metrics)
    if xgb_reg_metrics.get("r2") is not None and xgb_reg_metrics["r2"] >= rf_reg_metrics["r2"]:
        best_score = ("xgboost", xgb_reg_metrics)
    if xgb_clf_metrics.get("f1") is not None and xgb_clf_metrics["f1"] >= rf_clf_metrics["f1"]:
        best_pass = ("xgboost", xgb_clf_metrics)

    report = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": API_FEATURE_COLUMNS,
        "targets": {"score": TARGET_SCORE, "pass_fail": f"{TARGET_PASS} (1=at-risk)"},
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "random_forest": {
            "regression": rf_reg_metrics,
            "classification": {
                "accuracy": rf_clf_metrics["accuracy"],
                "f1": rf_clf_metrics["f1"],
            },
        },
        "xgboost": {
            "regression": xgb_reg_metrics,
            "classification": {
                "accuracy": xgb_clf_metrics["accuracy"],
                "f1": xgb_clf_metrics["f1"],
            },
        },
        "best": {
            "score_model": best_score[0],
            "score_file": f"performance_{best_score[0]}.joblib",
            "pass_model": best_pass[0],
            "pass_file": f"pass_fail_{best_pass[0]}.joblib",
        },
    }

    METRICS_JSON.write_text(json.dumps(report, indent=2))
    BEST_MODEL_JSON.write_text(json.dumps(report["best"], indent=2))
    print(f"\n[OK] Metrics: {METRICS_JSON}")
    print(f"[OK] Best models: score={best_score[0]} (R²={best_score[1]['r2']}), pass={best_pass[0]} (F1={best_pass[1]['f1']})")

    return report


def main() -> int:
    try:
        train_models()
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
