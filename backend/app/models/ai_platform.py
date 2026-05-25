"""Week 3 Day 7 — unified AI platform API models."""

from pydantic import BaseModel, Field

from app.models.analytics import AnalyticsDashboard
from app.models.explanation import ExplainResponse
from app.models.insights import InsightsResponse
from app.models.prediction import PredictRequest, PredictResponse
from app.models.recommendation import RecommendationItem
from app.models.study_plan import (
    DailyStudyPlannerResponse,
    PersonalizedRecommendationsRequest,
    SubjectScoreInput,
)


class RecommendRequest(PersonalizedRecommendationsRequest):
    """POST /recommend — profile + optional study plan."""

    include_study_plan: bool = True
    predicted_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: str | None = None


class RecommendResponse(BaseModel):
    recommendations: list[RecommendationItem]
    weak_subjects: list[SubjectScoreInput]
    revision_order: list[str]
    collaborative_insights: list[str]
    focus_message: str
    study_plan: DailyStudyPlannerResponse | None = None


class AnalyticsAPIResponse(AnalyticsDashboard):
    """GET /analytics — dashboard analytics payload."""


class AIPlatformStatus(BaseModel):
    version: str = "week3-v1"
    modules: dict[str, str]
    endpoints: dict[str, str]
    models_loaded: bool
    shap_available: bool
