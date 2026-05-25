from pydantic import BaseModel

from app.models.recommendation import RecommendationItem


class WeakSubject(BaseModel):
    subject: str
    score: float


class ChartPoint(BaseModel):
    label: str
    value: float


class DashboardResponse(BaseModel):
    performance_score: float
    study_hours_week: float
    weak_subjects: list[WeakSubject]
    ai_suggestions_count: int
    study_hours_by_day: list[ChartPoint]
    performance_trend: list[ChartPoint]
    subject_distribution: list[ChartPoint]
    recommendations: list[RecommendationItem]
