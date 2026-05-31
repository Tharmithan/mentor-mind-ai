"""Monitoring & feedback orchestration (Week 7 · Day 6)."""

from __future__ import annotations

from app.models.monitoring import (
    FeedbackEntry,
    FeedbackSubmitRequest,
    ImprovementLoopResponse,
    ModelMonitoringMetrics,
    MonitoringDashboard,
    SatisfactionSummary,
)
from app.monitoring.collector import FeedbackCollector
from app.monitoring.improvement import ImprovementLoop
from app.monitoring.model_monitor import ModelMonitor
from app.monitoring.satisfaction import SatisfactionTracker


class MonitoringService:
    @staticmethod
    def submit_feedback(req: FeedbackSubmitRequest) -> FeedbackEntry:
        entry = FeedbackCollector.submit(req)

        if req.category == "prediction":
            actual = req.metadata.get("actual_score")
            log_id = req.metadata.get("log_id")
            if log_id and actual is not None:
                ModelMonitor.record_actual(str(log_id), float(actual), req.rating)
            elif actual is not None:
                ModelMonitor.attach_feedback_to_latest(req.user_id, req.rating, float(actual))
            else:
                ModelMonitor.attach_feedback_to_latest(req.user_id, req.rating)

        return entry

    @staticmethod
    def user_feedback(user_id: str) -> list[FeedbackEntry]:
        return FeedbackCollector.list_for_user(user_id)

    @staticmethod
    def satisfaction(user_id: str) -> SatisfactionSummary:
        return SatisfactionTracker.summarize(user_id)

    @staticmethod
    def model_metrics() -> ModelMonitoringMetrics:
        return ModelMonitor.metrics()

    @staticmethod
    def improvements(user_id: str) -> ImprovementLoopResponse:
        return ImprovementLoop.analyze(user_id)

    @staticmethod
    def dashboard(user_id: str) -> MonitoringDashboard:
        return MonitoringDashboard(
            satisfaction=SatisfactionTracker.summarize(user_id),
            model_metrics=ModelMonitor.metrics(),
            recent_feedback=FeedbackCollector.list_for_user(user_id, limit=10),
            improvement=ImprovementLoop.analyze(user_id),
        )

    @staticmethod
    def log_prediction(
        user_id: str,
        predicted_score: float,
        prediction_label: str,
        model_version: str,
        inputs: dict,
    ) -> str:
        entry = ModelMonitor.log_prediction(
            user_id, predicted_score, prediction_label, model_version, inputs
        )
        return entry.log_id
