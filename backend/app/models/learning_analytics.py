"""Pydantic models for AI Learning Analytics (Week 7 · Day 3)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.analytics import RiskMeter
from app.models.common import ChartPoint


class SubjectMastery(BaseModel):
    subject: str
    score: float = Field(ge=0, le=100)
    mastery_level: str  # beginner | developing | proficient | mastered
    trend: str = "stable"  # up | down | stable
    delta: float = 0.0


class LearningInsight(BaseModel):
    category: str  # study_time | productivity | weakness | burnout | growth
    title: str
    description: str
    severity: str = "info"  # info | warning | success


class LearningPatterns(BaseModel):
    best_study_time: str
    best_study_days: list[str]
    productivity_pattern: str
    weak_learning_areas: list[str]
    strong_learning_areas: list[str]
    burnout_risk: float
    burnout_level: str


class LearningAnalyticsDashboard(BaseModel):
    user_id: str
    learning_efficiency: float = Field(ge=0, le=100)
    productivity_score: float = Field(ge=0, le=100)
    weekly_growth: list[ChartPoint]
    subject_mastery: list[SubjectMastery]
    progress_trends: list[ChartPoint]
    study_hours_by_day: list[ChartPoint]
    patterns: LearningPatterns
    insights: list[LearningInsight]
    risk_meter: RiskMeter
    summary: str
    generated_at: str
