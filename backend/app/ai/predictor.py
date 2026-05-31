"""Load Day 5 joblib models for /api/predict."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.models.prediction import (
    PredictRequest,
    PredictResponse,
    StudentRiskDetection,
    score_to_prediction,
    sleep_hours_to_wellness,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
ML_MODELS = Path(os.environ.get("ML_MODELS_DIR", str(REPO_ROOT / "ml-models")))
BEST_MODEL_JSON = ML_MODELS / "best_model.json"

_SCRIPTS = REPO_ROOT / "datasets" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from ml_features import API_FEATURE_COLUMNS, build_features_from_row  # noqa: E402


class MLPredictor:
    def __init__(self) -> None:
        self._score_bundle = None
        self._pass_bundle = None
        self._version = "heuristic-v0.1"
        self._load()

    def _load(self) -> None:
        if not BEST_MODEL_JSON.exists():
            return
        try:
            best = json.loads(BEST_MODEL_JSON.read_text())
            score_path = ML_MODELS / best.get("score_file", "performance_random_forest.joblib")
            pass_path = ML_MODELS / best.get("pass_file", "pass_fail_random_forest.joblib")
            if score_path.exists():
                self._score_bundle = joblib.load(score_path)
            if pass_path.exists():
                self._pass_bundle = joblib.load(pass_path)
            if self._score_bundle:
                ver = best.get("version", "v1")
                self._version = f"{best.get('score_model', 'ml')}-{ver}"
        except Exception:
            self._score_bundle = None
            self._pass_bundle = None

    @property
    def is_loaded(self) -> bool:
        return self._score_bundle is not None

    def _feature_vector(self, payload: PredictRequest) -> pd.DataFrame:
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

    def _student_risk(
        self,
        predicted: float,
        at_risk: bool,
        at_risk_prob: float,
        sleep_hours: float,
        study_hours: float,
    ) -> StudentRiskDetection:
        low_perf = float(np.clip(at_risk_prob * 100 if at_risk_prob else max(0, (58 - predicted) * 2), 0, 100))
        sleep_deficit = max(0, 7 - sleep_hours)
        burnout = float(np.clip(sleep_deficit * 20 + study_hours * 6, 0, 100))
        return StudentRiskDetection(
            high_risk=at_risk,
            low_performance_chance=round(low_perf, 1),
            burnout_probability=round(burnout, 1),
        )

    def _build_response(
        self,
        predicted: float,
        risk: str,
        recommendation: str,
        confidence_pct: float,
        at_risk: bool,
        version: str,
        student_risk: StudentRiskDetection,
    ) -> PredictResponse:
        return PredictResponse(
            prediction=score_to_prediction(predicted, at_risk),
            confidence=round(confidence_pct, 1),
            predicted_score=round(predicted, 1),
            risk_level=risk,
            recommendation=recommendation,
            model_version=version,
            student_risk=student_risk,
        )

    def predict(self, payload: PredictRequest) -> PredictResponse:
        if not self.is_loaded:
            return self._heuristic(payload)

        X = self._feature_vector(payload)
        score_model = self._score_bundle["model"]
        predicted = float(np.clip(score_model.predict(X)[0], 0, 100))

        at_risk = predicted < 60
        at_risk_prob = 0.5
        if self._pass_bundle:
            clf = self._pass_bundle["model"]
            proba = clf.predict_proba(X)[0]
            at_risk_prob = float(proba[1]) if len(proba) > 1 else float(clf.predict(X)[0])
            at_risk = at_risk_prob >= 0.5

        if predicted >= 75:
            risk = "low"
            recommendation = "On track — maintain current study pace."
        elif predicted >= 60:
            risk = "medium"
            recommendation = "Review weak topics and increase practice quizzes."
        else:
            risk = "high"
            recommendation = "At-risk — schedule extra study sessions and a mock interview."

        # Confidence 0–100: higher when model agrees and score is decisive
        confidence_pct = (1 - abs(at_risk_prob - 0.5) * 2) * 40 + min(abs(predicted - 50), 50) * 0.6 + 50
        confidence_pct = float(np.clip(confidence_pct, 55, 98))

        risk_det = self._student_risk(
            predicted, at_risk, at_risk_prob, payload.sleep_hours, payload.study_hours
        )
        return self._build_response(
            predicted, risk, recommendation, confidence_pct, at_risk, self._version, risk_det
        )

    def _heuristic(self, payload: PredictRequest) -> PredictResponse:
        weighted = (
            payload.prior_score * 0.5
            + payload.attendance_value * 0.3
            + min(payload.study_hours / 6 * 100, 100) * 0.2
        )
        quiz_bonus = min(payload.quizzes_completed * 2, 10)
        predicted = round(min(100, weighted + quiz_bonus), 1)
        at_risk = predicted < 60
        if predicted >= 75:
            risk, rec = "low", "On track — maintain current study pace."
        elif predicted >= 60:
            risk, rec = "medium", "Review weak topics and increase practice quizzes."
        else:
            risk, rec = "high", "At-risk — schedule extra study sessions."
        confidence_pct = min(92, 60 + predicted * 0.35)
        risk_det = self._student_risk(
            predicted, at_risk, 0.6 if at_risk else 0.25, payload.sleep_hours, payload.study_hours
        )
        return self._build_response(
            predicted, risk, rec, confidence_pct, at_risk, "heuristic-v0.1", risk_det
        )


_predictor: MLPredictor | None = None


def get_predictor() -> MLPredictor:
    global _predictor
    if _predictor is None:
        _predictor = MLPredictor()
    return _predictor
