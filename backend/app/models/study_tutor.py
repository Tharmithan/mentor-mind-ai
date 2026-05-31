"""Pydantic models for Study Agent tutor features (Week 6 · Day 2)."""

from pydantic import BaseModel, Field


class StudyPlanDay(BaseModel):
    day: int
    phase: str
    focus: str
    tasks: list[str]
    duration_hours: float = Field(ge=0.5, le=8)
    resources: list[str] = Field(default_factory=list)


class ExamStudyPlanRequest(BaseModel):
    subject: str = Field(min_length=1)
    days: int = Field(default=14, ge=1, le=90)
    hours_per_day: float = Field(default=2.0, ge=0.5, le=8)
    document_id: str | None = None


class ExamStudyPlanResponse(BaseModel):
    subject: str
    days: int
    hours_per_day: float
    summary: str
    phases: list[str]
    schedule: list[StudyPlanDay]
    tips: list[str]
    used_llm: bool = False


class RevisionPhase(BaseModel):
    week: int
    subjects: list[str]
    focus_topics: list[str]
    daily_hours: float
    tasks: list[str]


class RevisionPlanRequest(BaseModel):
    exam_subject: str | None = None
    days_until_exam: int = Field(default=14, ge=1, le=90)
    subject_scores: dict[str, float] | None = None


class RevisionPlanResponse(BaseModel):
    exam_subject: str | None
    days_until_exam: int
    weak_subjects: list[dict]
    revision_order: list[str]
    phases: list[RevisionPhase]
    summary: str


class LearningGoalCreate(BaseModel):
    title: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    target_days: int | None = Field(default=None, ge=1, le=365)
    target_date: str | None = None


class LearningGoalUpdate(BaseModel):
    progress_pct: float | None = Field(default=None, ge=0, le=100)
    completed_milestone: str | None = None
    note: str | None = None


class LearningGoal(BaseModel):
    id: str
    title: str
    subject: str
    target_days: int | None = None
    target_date: str | None = None
    progress_pct: float = 0
    milestones_completed: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class LearningGoalsResponse(BaseModel):
    session_id: str
    goals: list[LearningGoal]


class WeakSubjectAnalysis(BaseModel):
    subject: str
    score: float
    priority: str
    suggested_topics: list[str]
    resources: list[str]
    daily_minutes: int


class DailyStudyRecommendation(BaseModel):
    title: str
    description: str
    subject: str
    priority: str
    estimated_minutes: int


class DailyStudyRecommendationsResponse(BaseModel):
    summary: str
    weak_subjects: list[WeakSubjectAnalysis]
    recommendations: list[DailyStudyRecommendation]
    focus_areas: list[str]
    study_streak_tip: str
