"""Model monitoring — prediction accuracy & drift (Week 7 · Day 6)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.models.monitoring import ModelMonitoringMetrics, PredictionLogEntry
from app.monitoring.store import get_monitoring_store


class ModelMonitor:
    @staticmethod
    def log_prediction(
        user_id: str,
        predicted_score: float,
        prediction_label: str,
        model_version: str,
        inputs: dict,
    ) -> PredictionLogEntry:
        entry = PredictionLogEntry(
            log_id=uuid.uuid4().hex[:12],
            user_id=user_id,
            predicted_score=predicted_score,
            prediction_label=prediction_label,
            model_version=model_version,
            inputs=inputs,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        store = get_monitoring_store()
        logs = store.load_predictions()
        logs.append(entry.model_dump())
        store.save_predictions(logs[-1000:])
        return entry

    @staticmethod
    def record_actual(
        log_id: str,
        actual_score: float,
        feedback_rating: int | None = None,
    ) -> PredictionLogEntry | None:
        store = get_monitoring_store()
        logs = store.load_predictions()
        for e in logs:
            if e.get("log_id") != log_id:
                continue
            pred = e.get("predicted_score", 0)
            e["actual_score"] = actual_score
            e["error"] = round(abs(pred - actual_score), 2)
            if feedback_rating is not None:
                e["feedback_rating"] = feedback_rating
            store.save_predictions(logs)
            return PredictionLogEntry(**e)
        return None

    @staticmethod
    def attach_feedback_to_latest(
        user_id: str,
        feedback_rating: int,
        actual_score: float | None = None,
    ) -> PredictionLogEntry | None:
        store = get_monitoring_store()
        logs = store.load_predictions()
        for e in reversed(logs):
            if e.get("user_id") != user_id:
                continue
            e["feedback_rating"] = feedback_rating
            if actual_score is not None:
                pred = e.get("predicted_score", 0)
                e["actual_score"] = actual_score
                e["error"] = round(abs(pred - actual_score), 2)
            store.save_predictions(logs)
            return PredictionLogEntry(**e)
        return None

    @staticmethod
    def metrics() -> ModelMonitoringMetrics:
        store = get_monitoring_store()
        logs = store.load_predictions()
        if not logs:
            return ModelMonitoringMetrics(
                total_predictions=0,
                predictions_with_actuals=0,
                mean_absolute_error=None,
                avg_confidence=None,
                model_version=None,
                drift_status="stable",
                recent_accuracy_pct=None,
                last_prediction_at=None,
            )

        with_actuals = [e for e in logs if e.get("actual_score") is not None]
        errors = [e["error"] for e in with_actuals if e.get("error") is not None]
        mae = round(sum(errors) / len(errors), 2) if errors else None

        recent = logs[-20:]
        recent_errors = [e["error"] for e in recent if e.get("error") is not None]
        recent_acc = None
        if recent_errors:
            within_10 = sum(1 for err in recent_errors if err <= 10)
            recent_acc = round(100 * within_10 / len(recent_errors), 1)

        drift = "stable"
        if mae is not None:
            if mae > 15:
                drift = "alert"
            elif mae > 8:
                drift = "watch"

        versions = [e.get("model_version") for e in logs if e.get("model_version")]
        return ModelMonitoringMetrics(
            total_predictions=len(logs),
            predictions_with_actuals=len(with_actuals),
            mean_absolute_error=mae,
            avg_confidence=None,
            model_version=versions[-1] if versions else None,
            drift_status=drift,
            recent_accuracy_pct=recent_acc,
            last_prediction_at=logs[-1].get("created_at"),
        )
