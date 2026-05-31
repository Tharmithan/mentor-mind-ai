"""Pydantic models for Monitoring & Feedback Loop (Week 7 · Day 6)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FeedbackSubmitRequest(BaseModel):
    user_id: str = "demo-user-001"
    category: str  # recommendation | prediction | interview | general
    target_id: str = ""
    rating: int = Field(ge=1, le=5, description="1=not useful, 5=very useful")
    helpful: bool | None = None
    comment: str = ""
    metadata: dict = Field(default_factory=dict)


class FeedbackEntry(BaseModel):
    feedback_id: str
    user_id: str
    category: str
    target_id: str
    rating: int
    helpful: bool
    comment: str
    metadata: dict = Field(default_factory=dict)
    created_at: str


class SatisfactionSummary(BaseModel):
    user_id: str
    total_feedback: int
    avg_rating: float
    helpful_pct: float
    by_category: dict[str, dict]
    trend: str  # improving | stable | declining
    satisfaction_score: float = Field(description="0-100 composite score")


class PredictionLogEntry(BaseModel):
    log_id: str
    user_id: str
    predicted_score: float
    prediction_label: str
    model_version: str
    inputs: dict
    actual_score: float | None = None
    error: float | None = None
    feedback_rating: int | None = None
    created_at: str


class ModelMonitoringMetrics(BaseModel):
    total_predictions: int
    predictions_with_actuals: int
    mean_absolute_error: float | None
    avg_confidence: float | None
    model_version: str | None
    drift_status: str  # stable | watch | alert
    recent_accuracy_pct: float | None
    last_prediction_at: str | None


class ImprovementInsight(BaseModel):
    area: str
    issue: str
    action: str
    priority: str = "medium"


class ImprovementLoopResponse(BaseModel):
    user_id: str
    insights: list[ImprovementInsight]
    downranked_targets: list[str]
    improved_recommendation_note: str
    applied_adjustments: list[str]


class MonitoringDashboard(BaseModel):
    satisfaction: SatisfactionSummary
    model_metrics: ModelMonitoringMetrics
    recent_feedback: list[FeedbackEntry]
    improvement: ImprovementLoopResponse
