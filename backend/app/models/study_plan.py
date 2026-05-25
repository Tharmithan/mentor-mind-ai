from pydantic import BaseModel, Field

from app.models.recommendation import RecommendationItem


class SubjectScoreInput(BaseModel):
    subject: str
    score: float = Field(ge=0, le=100)


class PersonalizedRecommendationsRequest(BaseModel):
    """Input for rule-based + collaborative recommendations."""

    study_hours: float = Field(default=3.0, ge=0, le=24)
    attendance_pct: float = Field(default=80.0, ge=0, le=100)
    sleep_hours: float = Field(default=7.0, ge=0, le=24)
    past_failures: int = Field(default=0, ge=0, le=10)
    subject_scores: list[SubjectScoreInput] | None = None
    predicted_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: str | None = None


class FocusArea(BaseModel):
    subject: str
    topic: str
    score: float
    priority_rank: int


class TimetableSlot(BaseModel):
    day: str
    time_slot: str
    subject: str
    topic: str
    duration_hours: float
    priority: str
    task: str


class PersonalizedRecommendationsResponse(BaseModel):
    recommendations: list[RecommendationItem]
    weak_subjects: list[SubjectScoreInput]
    revision_order: list[str]
    collaborative_insights: list[str]
    focus_message: str


class DailyStudyPlannerResponse(BaseModel):
    """AI Daily Study Planner — timetable + priorities."""

    revision_priority: list[str]
    focus_areas: list[FocusArea]
    weekly_study_hours: float
    timetable: list[TimetableSlot]
    collaborative_insights: list[str]
    summary: str
    recommendations: list[RecommendationItem]
