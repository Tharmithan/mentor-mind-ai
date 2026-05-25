from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    study_hours: float = Field(ge=0, le=24, description="Daily study hours")
    attendance_pct: float = Field(ge=0, le=100, description="Attendance percentage")
    prior_score: float = Field(ge=0, le=100, description="Previous assessment score")
    quizzes_completed: int = Field(ge=0, default=0)


class PredictResponse(BaseModel):
    predicted_score: float
    risk_level: str
    confidence: float
    recommendation: str
    model_version: str = "mock-v0.1"
