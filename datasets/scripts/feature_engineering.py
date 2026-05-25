#!/usr/bin/env python3
"""
Day 4 — Feature engineering.

Creates custom features, tests importance, removes weak predictors,
exports ML-ready data to datasets/final/.

Usage:
  python datasets/scripts/feature_engineering.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "datasets"
PROCESSED = ROOT / "processed"
FINAL = ROOT / "final"

CLEANED_CSV = PROCESSED / "student_performance_cleaned.csv"
FEATURES_FULL_CSV = FINAL / "performance_features_full.csv"
ML_READY_CSV = FINAL / "performance_ml_ready.csv"
ML_READY_BEHAVIORAL_CSV = FINAL / "performance_ml_ready_behavioral.csv"
TRAIN_CSV = FINAL / "train.csv"
TEST_CSV = FINAL / "test.csv"
TRAIN_BEHAVIORAL_CSV = FINAL / "train_behavioral.csv"
TEST_BEHAVIORAL_CSV = FINAL / "test_behavioral.csv"

# Exclude prior grades when building behavioral-only model (MentorMind API use case)
GRADE_LEAKAGE_COLS = {"grade_period_1", "grade_period_2", "final_grade", "grade_momentum"}
IMPORTANCE_JSON = FINAL / "feature_importance.json"
REPORT_MD = FINAL / "feature_engineering_report.md"

TARGET = "performance_pct"

# Base numeric inputs (existing)
BASE_FEATURES = [
    "study_hours",
    "attendance_pct",
    "past_failures",
    "wellness_score",
    "absences",
    "grade_period_1",
    "grade_period_2",
    "family_relationship",
    "free_time",
    "going_out",
    "weekday_alcohol",
    "weekend_alcohol",
    "mother_education",
    "father_education",
    "travel_time",
    "gender",
    "school_support",
    "family_support",
    "extracurricular",
    "wants_higher_ed",
    "internet_access",
]

# Engineered feature names
ENGINEERED_FEATURES = [
    "consistency_score",
    "productivity_index",
    "exam_readiness_score",
    "assignment_completion_score",
    "grade_momentum",
    "study_efficiency",
]


def load_cleaned() -> pd.DataFrame:
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(f"Run clean_data.py first. Missing {CLEANED_CSV}")
    return pd.read_csv(CLEANED_CSV)


def _scale_0_100(series: pd.Series, lo: float | None = None, hi: float | None = None) -> pd.Series:
    lo = lo if lo is not None else series.min()
    hi = hi if hi is not None else series.max()
    if hi <= lo:
        return pd.Series(50.0, index=series.index)
    return ((series - lo) / (hi - lo) * 100).clip(0, 100)


def create_custom_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build consistency, productivity, and exam readiness scores."""
    out = df.copy()

    # Grade stability → consistency (low variance across G1, G2, G3 = high score)
    grade_std = out[["grade_period_1", "grade_period_2", "final_grade"]].std(axis=1)
    out["consistency_score"] = (100 - _scale_0_100(grade_std, 0, grade_std.quantile(0.95))).round(1)

    # Study output per failure → productivity
    raw_productivity = (out["study_hours"] * out["attendance_pct"] / 100) / (out["past_failures"] + 1)
    out["productivity_index"] = _scale_0_100(raw_productivity).round(1)

    # Assignments proxy: fewer past failures = better completion
    out["assignment_completion_score"] = (100 - out["past_failures"] * 25).clip(0, 100).round(1)

    # Exam readiness — user formula (scaled inputs 0–100)
    study_scaled = _scale_0_100(out["study_hours"], 0, 6)
    out["exam_readiness_score"] = (
        study_scaled * 0.4
        + out["attendance_pct"] * 0.3
        + out["assignment_completion_score"] * 0.3
    ).round(1)

    # Grade improvement G1 → final
    out["grade_momentum"] = (out["final_grade"] - out["grade_period_1"]).clip(-20, 20)
    out["grade_momentum_score"] = _scale_0_100(out["grade_momentum"], -10, 10).round(1)

    # Study efficiency (from Day 2 concept)
    out["study_efficiency"] = (out["study_hours"] / (out["past_failures"] + 1)).round(2)

    return out


def evaluate_feature_importance(
    df: pd.DataFrame,
    candidate_features: list[str],
    min_importance_ratio: float = 0.02,
) -> tuple[list[str], list[dict], dict]:
    """
    Random Forest feature importance → keep strong, drop weak.
    Weak = importance < min_importance_ratio * max importance.
    """
    available = [c for c in candidate_features if c in df.columns]
    X = df[available].fillna(0)
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=150, max_depth=14, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    test_r2 = float(model.score(X_test, y_test))

    importances = pd.Series(model.feature_importances_, index=available).sort_values(ascending=False)
    max_imp = importances.max()
    threshold = max_imp * min_importance_ratio

    ranked = []
    for feat, imp in importances.items():
        ranked.append(
            {
                "feature": feat,
                "importance": round(float(imp), 4),
                "importance_pct": round(float(imp / importances.sum() * 100), 2),
                "kept": bool(imp >= threshold),
                "engineered": feat in ENGINEERED_FEATURES,
            }
        )

    selected = [r["feature"] for r in ranked if r["kept"]]
    dropped = [r["feature"] for r in ranked if not r["kept"]]

    meta = {
        "model": "RandomForestRegressor",
        "test_r2": round(test_r2, 4),
        "threshold": round(float(threshold), 4),
        "features_evaluated": len(available),
        "features_kept": len(selected),
        "features_dropped": len(dropped),
        "dropped_features": dropped,
    }
    return selected, ranked, meta


def build_final_dataset(df: pd.DataFrame, selected_features: list[str]) -> pd.DataFrame:
    meta_cols = ["subject", "course", "at_risk", TARGET]
    meta_cols = [c for c in meta_cols if c in df.columns]
    cols = selected_features + meta_cols
    return df[cols].copy()


def write_report(
    ranked: list[dict],
    meta: dict,
    formulas: dict,
    ranked_beh: list[dict] | None = None,
    meta_beh: dict | None = None,
) -> None:
    lines = [
        "# Feature Engineering Report (Day 4)",
        "",
        f"*Generated: {datetime.now(timezone.utc).isoformat()}*",
        "",
        "## Custom features created",
        "",
        "| Feature | Formula / logic |",
        "|---------|-----------------|",
        f"| `consistency_score` | {formulas['consistency_score']} |",
        f"| `productivity_index` | {formulas['productivity_index']} |",
        f"| `exam_readiness_score` | {formulas['exam_readiness_score']} |",
        f"| `assignment_completion_score` | {formulas['assignment_completion_score']} |",
        f"| `grade_momentum_score` | {formulas['grade_momentum']} |",
        "",
        "## Feature selection (Random Forest)",
        "",
        f"- Features evaluated: **{meta['features_evaluated']}**",
        f"- Features kept: **{meta['features_kept']}**",
        f"- Features dropped: **{meta['features_dropped']}**",
        f"- Hold-out R²: **{meta['test_r2']}**",
        "",
        "### Kept (ranked by importance)",
        "",
        "| Rank | Feature | Importance % | Engineered |",
        "|------|---------|--------------|------------|",
    ]
    for i, r in enumerate([x for x in ranked if x["kept"]], 1):
        eng = "yes" if r["engineered"] else "no"
        lines.append(f"| {i} | `{r['feature']}` | {r['importance_pct']}% | {eng} |")

    if meta["dropped_features"]:
        lines.extend(["", "### Dropped (weak features)", ""])
        for f in meta["dropped_features"]:
            lines.append(f"- `{f}`")

    if ranked_beh and meta_beh:
        lines.extend(
            [
                "",
                "## Behavioral model (no prior grades — MentorMind API)",
                "",
                f"- Features kept: **{meta_beh['features_kept']}** · R²: **{meta_beh['test_r2']}**",
                "",
                "| Rank | Feature | Importance % |",
                "|------|---------|--------------|",
            ]
        )
        for i, r in enumerate([x for x in ranked_beh if x["kept"]][:8], 1):
            lines.append(f"| {i} | `{r['feature']}` | {r['importance_pct']}% |")

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "| File | Description |",
            "|------|-------------|",
            "| `performance_features_full.csv` | All base + engineered features |",
            "| `performance_ml_ready.csv` | Selected (includes grades if strong) |",
            "| `performance_ml_ready_behavioral.csv` | Study/attendance/readiness only |",
            "| `train.csv` / `test.csv` | 80/20 split |",
            "| `train_behavioral.csv` | Behavioral split for API-style model |",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines))


def run_feature_engineering(test_size: float = 0.2) -> dict:
    print("=== Day 4: Feature Engineering ===\n")

    df = load_cleaned()
    print(f"Loaded {len(df)} rows\n")

    df = create_custom_features(df)
    print("Created custom features:")
    for f in ENGINEERED_FEATURES + ["grade_momentum_score"]:
        if f in df.columns:
            print(f"  • {f}: mean={df[f].mean():.1f}")

    all_engineered = ENGINEERED_FEATURES + ["grade_momentum_score"]
    candidate = BASE_FEATURES + [f for f in all_engineered if f in df.columns]

    print(f"\nEvaluating {len(candidate)} candidate features...")
    selected, ranked, meta = evaluate_feature_importance(df, candidate)

    FINAL.mkdir(parents=True, exist_ok=True)
    df.to_csv(FEATURES_FULL_CSV, index=False)
    print(f"\n[OK] Full features: {FEATURES_FULL_CSV}")

    ml_ready = build_final_dataset(df, selected)
    ml_ready.to_csv(ML_READY_CSV, index=False)
    print(f"[OK] ML-ready ({len(selected)} features): {ML_READY_CSV}")

    train, test = train_test_split(ml_ready, test_size=test_size, random_state=42)
    train.to_csv(TRAIN_CSV, index=False)
    test.to_csv(TEST_CSV, index=False)
    print(f"[OK] Train: {TRAIN_CSV} ({len(train)} rows)")
    print(f"[OK] Test:  {TEST_CSV} ({len(test)} rows)")

    # Behavioral-only: no prior grade columns (exam_readiness, study_hours, etc.)
    behavioral_candidates = [c for c in candidate if c not in GRADE_LEAKAGE_COLS]
    print(f"\nBehavioral feature selection ({len(behavioral_candidates)} candidates)...")
    sel_beh, ranked_beh, meta_beh = evaluate_feature_importance(df, behavioral_candidates)
    ml_beh = build_final_dataset(df, sel_beh)
    ml_beh.to_csv(ML_READY_BEHAVIORAL_CSV, index=False)
    print(f"[OK] Behavioral ML-ready ({len(sel_beh)} features): {ML_READY_BEHAVIORAL_CSV}")
    tr_b, te_b = train_test_split(ml_beh, test_size=test_size, random_state=42)
    tr_b.to_csv(TRAIN_BEHAVIORAL_CSV, index=False)
    te_b.to_csv(TEST_BEHAVIORAL_CSV, index=False)
    print(f"[OK] Train behavioral: {TRAIN_BEHAVIORAL_CSV} ({len(tr_b)} rows)")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selection": meta,
        "behavioral_selection": meta_beh,
        "ranked_features": ranked,
        "ranked_features_behavioral": ranked_beh,
        "selected_features": selected,
        "selected_features_behavioral": sel_beh,
        "engineered_features": all_engineered,
    }
    IMPORTANCE_JSON.write_text(json.dumps(report, indent=2))

    formulas = {
        "consistency_score": "100 − scaled std(G1, G2, G3) — stable grades = high consistency",
        "productivity_index": "scale(study_hours × attendance% / (failures + 1))",
        "exam_readiness_score": "study_scaled×0.4 + attendance×0.3 + assignment_completion×0.3",
        "assignment_completion_score": "100 − past_failures×25 (capped 0–100)",
        "grade_momentum": "scale(final_grade − G1) — improvement signal",
    }
    write_report(ranked, meta, formulas, ranked_beh, meta_beh)
    print(f"[OK] Report: {REPORT_MD}")
    print(f"[OK] Importance: {IMPORTANCE_JSON}")

    print("\n--- Top 5 features ---")
    for r in ranked[:5]:
        print(f"  {r['feature']}: {r['importance_pct']}%")

    if meta["dropped_features"]:
        print(f"\n--- Dropped {len(meta['dropped_features'])} weak features ---")
        print(f"  {', '.join(meta['dropped_features'][:8])}{'...' if len(meta['dropped_features']) > 8 else ''}")

    return report


def main() -> int:
    try:
        run_feature_engineering()
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
