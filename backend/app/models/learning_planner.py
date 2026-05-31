"""Pydantic models for Personalized Learning Planner (Week 6 · Day 5)."""

from pydantic import BaseModel, Field


class MonthlyTopic(BaseModel):
    name: str
    description: str
    resources: list[str] = Field(default_factory=list)


class MonthlyPhase(BaseModel):
    month: int
    title: str
    topics: list[MonthlyTopic]
    goals: list[str]
    hours_per_week: float = 10.0
    milestone: str


class WeeklyTask(BaseModel):
    week: int
    focus: str
    tasks: list[str]
    hours: float


class MilestoneStatus(BaseModel):
    id: str
    label: str
    month: int
    completed: bool = False
    completed_at: str | None = None


class LearningRoadmapRequest(BaseModel):
    goal: str = Field(min_length=3)
    hours_per_week: float = Field(default=10.0, ge=2, le=40)
    total_months: int | None = Field(default=None, ge=1, le=12)


class LearningRoadmapResponse(BaseModel):
    goal: str
    career_id: str
    career_title: str
    total_months: int
    hours_per_week: float
    summary: str
    months: list[MonthlyPhase]
    milestones: list[MilestoneStatus]


class CreateLearningPlanRequest(BaseModel):
    goal: str = Field(min_length=3)
    hours_per_week: float = Field(default=10.0, ge=2, le=40)
    user_id: str | None = None


class LearningPlanProgressUpdate(BaseModel):
    milestone_id: str | None = None
    current_month: int | None = Field(default=None, ge=1)
    current_week: int | None = Field(default=None, ge=1, le=4)
    progress_pct: float | None = Field(default=None, ge=0, le=100)
    note: str | None = None


class LearningPlanResponse(BaseModel):
    plan_id: str
    goal: str
    career_title: str
    progress_pct: float
    current_month: int
    current_week: int
    hours_per_week: float
    roadmap: LearningRoadmapResponse
    milestones: list[MilestoneStatus]
    created_at: str
    updated_at: str


class WeeklyPlanResponse(BaseModel):
    plan_id: str
    month: int
    month_title: str
    week: int
    progress_pct: float
    weeks: list[WeeklyTask]
    summary: str
