from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    """Day 7 ML API input — frontend sends study, attendance, sleep."""

    study_hours: float = Field(ge=0, le=24, description="Daily study hours")
    attendance: float = Field(ge=0, le=100, description="Attendance percentage")
    attendance_pct: float | None = Field(
        default=None, ge=0, le=100, description="Alias for attendance"
    )
    sleep_hours: float = Field(
        default=7, ge=0, le=24, description="Sleep hours (maps to wellness proxy)"
    )
    prior_score: float = Field(default=70, ge=0, le=100, description="Previous assessment %")
    quizzes_completed: int = Field(default=10, ge=0)

    @field_validator("attendance_pct", mode="before")
    @classmethod
    def default_attendance_pct(cls, v, info):
        if v is not None:
            return v
        att = info.data.get("attendance")
        return att if att is not None else 80.0

    @property
    def attendance_value(self) -> float:
        return self.attendance_pct if self.attendance_pct is not None else self.attendance


class StudentRiskDetection(BaseModel):
    """Week 2 — Student Risk Detection (recruiter-facing)."""

    high_risk: bool = Field(description="True if student is at-risk of failing")
    low_performance_chance: float = Field(
        ge=0, le=100, description="% chance of performance below 60%"
    )
    burnout_probability: float = Field(
        ge=0, le=100, description="% estimated burnout from sleep/study load"
    )


class PredictResponse(BaseModel):
    """Day 7 ML API output."""

    prediction: str = Field(
        description='e.g. "High Performance", "Medium Performance", "At Risk"'
    )
    confidence: float = Field(ge=0, le=100, description="Confidence 0–100%")
    predicted_score: float = Field(description="Numeric score 0–100")
    risk_level: str = Field(description="low | medium | high")
    recommendation: str
    model_version: str = "heuristic-v0.1"
    student_risk: StudentRiskDetection
    monitoring_log_id: str | None = Field(
        default=None, description="ID for submitting prediction accuracy feedback"
    )


def sleep_hours_to_wellness(sleep_hours: float) -> float:
    """Map sleep hours (4–10 typical) to wellness proxy 1–5."""
    return float(max(1, min(5, round(sleep_hours / 2))))


def score_to_prediction(predicted_score: float, at_risk: bool) -> str:
    if predicted_score >= 75:
        return "High Performance"
    if predicted_score >= 60:
        return "Medium Performance"
    if at_risk or predicted_score < 50:
        return "At Risk"
    return "Low Performance"
