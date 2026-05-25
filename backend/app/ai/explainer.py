"""Week 3 Day 6 — SHAP + feature importance explainability for ML predictions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.models.prediction import PredictRequest, sleep_hours_to_wellness

REPO_ROOT = Path(__file__).resolve().parents[3]
ML_MODELS = REPO_ROOT / "ml-models"
BEST_MODEL_JSON = ML_MODELS / "best_model.json"
CLEANED_CSV = REPO_ROOT / "datasets" / "processed" / "student_performance_cleaned.csv"
GLOBAL_SHAP_JSON = REPO_ROOT / "results" / "metrics" / "shap_global.json"

_SCRIPTS = REPO_ROOT / "datasets" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ml_features import API_FEATURE_COLUMNS, build_features_from_row, add_api_features, features_dataframe  # noqa: E402

FEATURE_LABELS = {
    "study_hours": "Study hours",
    "attendance_pct": "Attendance",
    "past_failures": "Past failures",
    "assignment_completion_score": "Assignment completion",
    "exam_readiness_score": "Exam readiness",
    "productivity_index": "Productivity index",
    "consistency_score": "Consistency",
    "wellness_score": "Wellness (sleep proxy)",
}


def _feature_vector(payload: PredictRequest) -> pd.DataFrame:
    past_failures = max(0, min(3, (20 - payload.quizzes_completed) // 5))
    wellness = sleep_hours_to_wellness(payload.sleep_hours)
    feats = build_features_from_row(
        study_hours=payload.study_hours,
        attendance_pct=payload.attendance_value,
        past_failures=past_failures,
        prior_score=payload.prior_score,
        consistency_score=min(100, payload.prior_score),
        wellness_score=wellness,
    )
    return pd.DataFrame([feats])[API_FEATURE_COLUMNS]


def _load_background(n: int = 200) -> pd.DataFrame:
    if CLEANED_CSV.exists():
        df = add_api_features(pd.read_csv(CLEANED_CSV))
        X = features_dataframe(df)
        return X.sample(min(n, len(X)), random_state=42)
    return pd.DataFrame(
        np.random.rand(min(n, 50), len(API_FEATURE_COLUMNS)),
        columns=API_FEATURE_COLUMNS,
    )


def _shap_contributions(model, X: pd.DataFrame, background: pd.DataFrame, at_risk: bool) -> dict[str, float] | None:
    try:
        import shap
    except ImportError:
        return None

    try:
        explainer = shap.TreeExplainer(model, data=background, feature_perturbation="interventional")
        exp = explainer(X, check_additivity=False)
        sv = exp.values
        if sv.ndim == 3:
            row = np.array(sv[0, :, 1] if at_risk else sv[0, :, 0])
        else:
            row = np.array(sv[0])
        return {API_FEATURE_COLUMNS[i]: float(row[i]) for i in range(len(API_FEATURE_COLUMNS))}
    except Exception:
        try:
            explainer = shap.Explainer(model, background)
            exp = explainer(X)
            row = exp.values[0]
            return {API_FEATURE_COLUMNS[i]: float(row[i]) for i in range(len(API_FEATURE_COLUMNS))}
        except Exception:
            return None


def _importance_fallback(model, X: pd.DataFrame, background: pd.DataFrame) -> dict[str, float]:
    if not hasattr(model, "feature_importances_"):
        return {f: 1.0 for f in API_FEATURE_COLUMNS}
    imp = model.feature_importances_
    means = background.mean()
    deltas = (X.iloc[0] - means).abs()
    weighted = imp * (1 + deltas.values)
    total = weighted.sum() or 1
    return {
        API_FEATURE_COLUMNS[i]: float(weighted[i] / total)
        for i in range(len(API_FEATURE_COLUMNS))
    }


def _to_contribution_pct(raw: dict[str, float], predicted_low: bool) -> list[dict]:
    """Convert SHAP or importance weights to % contributions toward outcome."""
    items = []
    for feat, val in raw.items():
        # Features pushing toward low performance: negative SHAP on score, positive on at-risk
        if predicted_low:
            impact = -val if abs(val) < 10 else val  # heuristic for score vs clf
            direction = "negative" if impact > 0 else "positive"
        else:
            impact = val
            direction = "positive" if impact > 0 else "negative"
        items.append(
            {
                "feature": feat,
                "label": FEATURE_LABELS.get(feat, feat),
                "raw_value": round(float(val), 4),
                "impact": abs(float(val)),
                "direction": direction,
            }
        )
    total = sum(i["impact"] for i in items) or 1
    for i in items:
        i["contribution_pct"] = round(i["impact"] / total * 100, 1)
    items.sort(key=lambda x: x["contribution_pct"], reverse=True)
    return items


def _human_sentences(
    contributions: list[dict],
    predicted_low: bool,
    predicted_score: float,
    X: pd.DataFrame,
    background: pd.DataFrame,
) -> list[str]:
    medians = background.median()
    row = X.iloc[0]
    sentences = []
    outcome = "low performance" if predicted_low else "higher performance"

    for c in contributions[:5]:
        if c["contribution_pct"] < 8:
            continue
        feat = c["feature"]
        val = float(row[feat])
        med = float(medians[feat])
        label = c["label"]

        if predicted_low and val < med:
            qualifier = "High" if feat == "past_failures" else "Low"
            sentences.append(
                f"{qualifier} {label.lower()} contributed {c['contribution_pct']}% to predicted {outcome}."
            )
        elif not predicted_low and val >= med:
            sentences.append(
                f"Strong {label.lower()} supported this prediction ({c['contribution_pct']}% contribution)."
            )
        else:
            sentences.append(
                f"{label} had a {c['contribution_pct']}% influence on the model output."
            )

    top = contributions[0]
    summary = (
        f"Predicted score {predicted_score:.0f}%. "
        f"{top['label']} contributed {top['contribution_pct']}% "
        f"to predicted {'risk' if predicted_low else 'success'}."
    )
    return [summary] + sentences[:4]


class ModelExplainer:
    def __init__(self) -> None:
        self._score_bundle = None
        self._pass_bundle = None
        self._background: pd.DataFrame | None = None
        self._algorithm = "heuristic"
        self._load()

    def _load(self) -> None:
        if not BEST_MODEL_JSON.exists():
            return
        try:
            best = json.loads(BEST_MODEL_JSON.read_text())
            score_path = ML_MODELS / best.get("score_file", "")
            pass_path = ML_MODELS / best.get("pass_file", "")
            if score_path.exists():
                self._score_bundle = joblib.load(score_path)
            if pass_path.exists():
                self._pass_bundle = joblib.load(pass_path)
            self._algorithm = best.get("score_model", "ml")
        except Exception:
            pass

    def _background_data(self) -> pd.DataFrame:
        if self._background is None:
            self._background = _load_background()
        return self._background

    def explain(self, payload: PredictRequest, predicted_score: float, at_risk: bool) -> dict:
        X = _feature_vector(payload)
        bg = self._background_data()
        predicted_low = at_risk or predicted_score < 60

        model = None
        if self._pass_bundle and predicted_low:
            model = self._pass_bundle["model"]
        elif self._score_bundle:
            model = self._score_bundle["model"]

        raw: dict[str, float] | None = None
        method = "feature_importance"
        if model is not None:
            raw = _shap_contributions(model, X, bg, at_risk)
            if raw is not None:
                method = "shap"

        if raw is None and model is not None:
            raw = _importance_fallback(model, X, bg)
            method = "feature_importance"

        if raw is None:
            raw = {f: 1.0 / len(API_FEATURE_COLUMNS) for f in API_FEATURE_COLUMNS}
            method = "heuristic"

        contributions = _to_contribution_pct(raw, predicted_low)
        sentences = _human_sentences(contributions, predicted_low, predicted_score, X, bg)

        return {
            "method": method,
            "algorithm": self._algorithm,
            "predicted_score": predicted_score,
            "at_risk": at_risk,
            "contributions": contributions,
            "explanations": sentences,
            "top_feature": contributions[0]["feature"] if contributions else None,
        }

    def global_importance(self) -> dict | None:
        if GLOBAL_SHAP_JSON.exists():
            return json.loads(GLOBAL_SHAP_JSON.read_text())
        return None


_explainer: ModelExplainer | None = None


def get_explainer() -> ModelExplainer:
    global _explainer
    if _explainer is None:
        _explainer = ModelExplainer()
    return _explainer
