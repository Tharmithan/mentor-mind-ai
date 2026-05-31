"""Pydantic models for Career Agent (Week 6 · Day 3)."""

from pydantic import BaseModel, Field


class StudentCareerProfile(BaseModel):
    """Aggregated signals for career matching."""

    subject_scores: dict[str, float] = Field(default_factory=dict)
    performance_score: float = 0.0
    interview_overall: float | None = None
    interview_technical: float | None = None
    interview_communication: float | None = None
    interview_confidence: float | None = None
    interests: list[str] = Field(default_factory=list)
    skills: dict[str, float] = Field(default_factory=dict)


class CareerMatch(BaseModel):
    career_id: str
    title: str
    match_score: float = Field(ge=0, le=100)
    rationale: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class CareerRecommendationResponse(BaseModel):
    top_career: CareerMatch
    alternatives: list[CareerMatch]
    profile_summary: str
    analyzed: dict
    used_llm: bool = False


class SkillGapItem(BaseModel):
    skill: str
    current_level: float = Field(ge=0, le=100)
    required_level: float = Field(ge=0, le=100)
    gap: float
    priority: str
    learning_actions: list[str]


class SkillGapAnalysisResponse(BaseModel):
    target_career: str
    overall_readiness: float
    gaps: list[SkillGapItem]
    summary: str


class RoadmapPhase(BaseModel):
    phase: str
    duration_weeks: int
    goals: list[str]
    skills: list[str]
    resources: list[str]


class LearningRoadmapResponse(BaseModel):
    career: str
    total_weeks: int
    phases: list[RoadmapPhase]
    summary: str
    milestones: list[str]


class IndustryTrend(BaseModel):
    title: str
    category: str
    relevance: str
    impact: str
    action: str


class IndustryTrendsResponse(BaseModel):
    trends: list[IndustryTrend]
    summary: str
    hot_roles: list[str]


class CareerAnalysisRequest(BaseModel):
    interests: list[str] | None = None
    target_career: str | None = None
    subject_scores: dict[str, float] | None = None
    interview_session_id: str | None = None
