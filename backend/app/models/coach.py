"""Pydantic models for AI Coach Dashboard (Week 6 · Day 7)."""

from pydantic import BaseModel, Field

from app.models.common import ChartPoint
from app.models.career import SkillGapItem


class CoachScoreCard(BaseModel):
    label: str
    score: float = Field(ge=0, le=100)
    delta: float = 0.0
    trend: str = "neutral"  # up | down | neutral
    subtitle: str = ""


class CoachRecommendation(BaseModel):
    id: str
    title: str
    description: str
    agent: str
    priority: str = "medium"
    action_path: str | None = None


class SkillGapOverview(BaseModel):
    target_career: str
    current_skills: list[str]
    missing_skills: list[str]
    overall_readiness: float
    gaps: list[SkillGapItem]


class CoachCharts(BaseModel):
    skill_growth: list[ChartPoint]
    learning_progress: list[ChartPoint]
    interview_improvement: list[ChartPoint]
    career_readiness_trend: list[ChartPoint]


class WeeklyProgressReport(BaseModel):
    week_label: str
    achievements: list[str]
    weaknesses: list[str]
    next_week_plan: list[str]
    generated_at: str


class CoachOverviewResponse(BaseModel):
    scores: list[CoachScoreCard]
    charts: CoachCharts
    skill_gap: SkillGapOverview
    recommendations: list[CoachRecommendation]
    weekly_report: WeeklyProgressReport
    target_career: str
    profile_summary: str
