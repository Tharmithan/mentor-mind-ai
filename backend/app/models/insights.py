from pydantic import BaseModel, Field

from app.models.study_plan import SubjectScoreInput


class InsightsRequest(BaseModel):
    study_hours: float = Field(default=3.0, ge=0, le=24)
    attendance_pct: float = Field(default=80.0, ge=0, le=100)
    sleep_hours: float = Field(default=7.0, ge=0, le=24)
    subject_scores: list[SubjectScoreInput] | None = None
    previous_attendance_pct: float | None = Field(default=None, ge=0, le=100)
    previous_subject_scores: list[SubjectScoreInput] | None = None


class AIInsight(BaseModel):
    id: str
    category: str
    message: str
    severity: str
    metric: str | None = None
    trend_direction: str | None = None
    impact_pct: float | None = None


class PerformanceSummary(BaseModel):
    headline: str
    overall_score: float
    trend_label: str
    highlights: list[str]
    summary_text: str


class InsightsResponse(BaseModel):
    generated_at: str
    insights: list[AIInsight]
    trends: list[AIInsight]
    performance_summary: PerformanceSummary
    cohort_stats: dict


class InsightsReportResponse(BaseModel):
    generated_at: str
    natural_language_report: str
    llm_enhanced: bool
    performance_summary: PerformanceSummary
    insights: list[AIInsight]
