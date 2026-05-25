#!/usr/bin/env python3
"""
Week 3 Day 6 — SHAP explainability + feature importance plots.

Outputs:
  results/metrics/shap_global.json
  results/graphs/shap_summary.png
  results/graphs/shap_feature_importance.png
  results/reports/model_explainability_report.md

Usage:
  python datasets/scripts/explain_model.py
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

REPO_ROOT = Path(__file__).resolve().parents[2]
ML_MODELS = REPO_ROOT / "ml-models"
PROCESSED = REPO_ROOT / "datasets" / "processed"
RESULTS = REPO_ROOT / "results"
METRICS_DIR = RESULTS / "metrics"
GRAPHS_DIR = RESULTS / "graphs"
REPORTS_DIR = RESULTS / "reports"
BEST_JSON = ML_MODELS / "best_model.json"
CLEANED = PROCESSED / "student_performance_cleaned.csv"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ml_features import API_FEATURE_COLUMNS, add_api_features, features_dataframe, TARGET_PASS  # noqa: E402

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


def _load_model():
    best = json.loads(BEST_JSON.read_text())
    path = ML_MODELS / best.get("pass_file", "pass_fail_random_forest.joblib")
    bundle = joblib.load(path)
    return bundle["model"], best.get("pass_model", "model")


def run_shap_analysis():
    print("=== Week 3 Day 6: Model Explainability (SHAP) ===\n")
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df = add_api_features(pd.read_csv(CLEANED))
    X = features_dataframe(df)
    y = df[TARGET_PASS]
    X_sample = X.sample(min(300, len(X)), random_state=42)

    model, algorithm = _load_model()
    print(f"Model: {algorithm} | Samples: {len(X_sample)}\n")

    try:
        import shap
    except ImportError:
        print("[ERROR] pip install shap")
        return 1

    bg = X_sample.iloc[:200]
    explainer = shap.TreeExplainer(model, data=bg, feature_perturbation="interventional")
    exp = explainer(bg, check_additivity=False)
    shap_values = exp.values
    if shap_values.ndim == 3:
        shap_values = shap_values[:, :, 1]

    sv = shap_values
    mean_abs = np.abs(sv).mean(axis=0)
    total = mean_abs.sum() or 1
    ranked = []
    for i, feat in enumerate(API_FEATURE_COLUMNS):
        ranked.append(
            {
                "feature": feat,
                "label": FEATURE_LABELS.get(feat, feat),
                "mean_abs_shap": round(float(mean_abs[i]), 4),
                "contribution_pct": round(float(mean_abs[i] / total * 100), 1),
                "direction": "risk",
            }
        )
    ranked.sort(key=lambda x: x["contribution_pct"], reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "shap",
        "algorithm": algorithm,
        "samples": len(X_sample),
        "mean_abs_shap": ranked,
    }
    (METRICS_DIR / "shap_global.json").write_text(json.dumps(payload, indent=2))

    plt.figure(figsize=(10, 6))
    shap.summary_plot(sv, bg, feature_names=[FEATURE_LABELS.get(f, f) for f in API_FEATURE_COLUMNS], show=False)
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / "shap_summary.png", dpi=120, bbox_inches="tight")
    plt.close()

    imp_series = pd.Series(mean_abs, index=[FEATURE_LABELS.get(f, f) for f in API_FEATURE_COLUMNS]).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    imp_series.plot(kind="barh", ax=ax, color="#8b5cf6")
    ax.set_xlabel("Mean |SHAP|")
    ax.set_title("Global Feature Importance (SHAP)")
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "shap_feature_importance.png", dpi=120)
    plt.close()

    top = ranked[0]
    lines = [
        "# Model Explainability Report",
        "",
        f"*Generated: {payload['generated_at']}*",
        "",
        "## Top global drivers (at-risk prediction)",
        "",
        f"**{top['label']}** — {top['contribution_pct']}% mean SHAP impact",
        "",
        "| Feature | SHAP % |",
        "|---------|--------|",
    ]
    for r in ranked:
        lines.append(f"| {r['label']} | {r['contribution_pct']}% |")
    lines.extend(
        [
            "",
            "## Plots",
            "",
            "- `results/graphs/shap_summary.png`",
            "- `results/graphs/shap_feature_importance.png`",
            "",
            "## Example explanation",
            "",
            f'"Low {ranked[1]["label"].lower()} contributed {ranked[1]["contribution_pct"]}% to predicted low performance."',
            "",
        ]
    )
    (REPORTS_DIR / "model_explainability_report.md").write_text("\n".join(lines))

    print(f"[OK] {METRICS_DIR / 'shap_global.json'}")
    print(f"[OK] {GRAPHS_DIR / 'shap_summary.png'}")
    print(f"[OK] Top: {top['label']} ({top['contribution_pct']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(run_shap_analysis())
