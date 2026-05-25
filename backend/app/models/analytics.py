from pydantic import BaseModel, Field

from app.models.common import ChartPoint


class RiskMeter(BaseModel):
    """AI Risk Meter — 0–100 where higher = more risk (engagement inverted)."""

    burnout_risk: float = Field(ge=0, le=100)
    exam_failure_risk: float = Field(ge=0, le=100)
    low_engagement_score: float = Field(ge=0, le=100, description="Risk from low engagement")


class AnalyticsCards(BaseModel):
    ai_score: float = Field(ge=0, le=100)
    risk_level: str
    performance_trend_delta: float = Field(description="Points change vs last week")
    study_streak_days: int = Field(ge=0)


class AnalyticsDashboard(BaseModel):
    cards: AnalyticsCards
    risk_meter: RiskMeter
    weekly_progress: list[ChartPoint]
    subject_comparison: list[ChartPoint]
    confidence_trends: list[ChartPoint]
