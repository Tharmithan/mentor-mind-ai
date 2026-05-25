"""Shared feature builder for training and API inference."""

from __future__ import annotations

import numpy as np
import pandas as pd

# Features aligned with MentorMind PredictRequest + Day 4 engineering
API_FEATURE_COLUMNS = [
    "study_hours",
    "attendance_pct",
    "past_failures",
    "assignment_completion_score",
    "exam_readiness_score",
    "productivity_index",
    "consistency_score",
    "wellness_score",
]

TARGET_SCORE = "performance_pct"
TARGET_PASS = "at_risk"  # 1 = fail/at-risk, 0 = pass


def _scale_0_100(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 50.0
    return float(np.clip((value - lo) / (hi - lo) * 100, 0, 100))


def failures_from_quizzes(quizzes_completed: int) -> int:
    """Map quiz count to past_failures proxy (0–3)."""
    return int(np.clip((20 - quizzes_completed) // 5, 0, 3))


def build_features_from_row(
    study_hours: float,
    attendance_pct: float,
    past_failures: int | None = None,
    quizzes_completed: int | None = None,
    wellness_score: float = 3.0,
    consistency_score: float | None = None,
    prior_score: float | None = None,
) -> dict[str, float]:
    """Build model input features from API-style fields."""
    if past_failures is None:
        past_failures = failures_from_quizzes(quizzes_completed or 10)

    assignment = float(np.clip(100 - past_failures * 25, 0, 100))
    study_scaled = _scale_0_100(study_hours, 0, 6)
    exam_readiness = study_scaled * 0.4 + attendance_pct * 0.3 + assignment * 0.3
    productivity = _scale_0_100(
        (study_hours * attendance_pct / 100) / (past_failures + 1), 0, 10
    )
    if consistency_score is None:
        consistency_score = float(prior_score) if prior_score is not None else 70.0

    return {
        "study_hours": float(study_hours),
        "attendance_pct": float(attendance_pct),
        "past_failures": float(past_failures),
        "assignment_completion_score": assignment,
        "exam_readiness_score": round(exam_readiness, 1),
        "productivity_index": round(productivity, 1),
        "consistency_score": float(consistency_score),
        "wellness_score": float(wellness_score),
    }


def add_api_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add/ensure API feature columns on cleaned dataframe."""
    rows = []
    for _, r in df.iterrows():
        rows.append(
            build_features_from_row(
                study_hours=r["study_hours"],
                attendance_pct=r["attendance_pct"],
                past_failures=int(r["past_failures"]),
                wellness_score=float(r.get("wellness_score", 3)),
                consistency_score=float(r.get("consistency_score", 70)),
                prior_score=float(r.get("grade_period_1", 50)) / 20 * 100,
            )
        )
    feat = pd.DataFrame(rows)
    out = df.copy()
    for col in API_FEATURE_COLUMNS:
        out[col] = feat[col]
    return out


def features_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    return df[API_FEATURE_COLUMNS].copy()
