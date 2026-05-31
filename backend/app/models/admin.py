"""Admin dashboard models (Week 8 · Bonus)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AdminUserSummary(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: str | None = None


class AdminOverviewResponse(BaseModel):
    total_users: int
    total_predictions: int
    total_feedback: int
    models_loaded: bool
    production_model_version: str | None = None
    vector_documents: int = 0
    active_interview_sessions: int = 0
    avg_satisfaction: float | None = None
    recent_users: list[AdminUserSummary] = Field(default_factory=list)
    system_status: dict[str, str] = Field(default_factory=dict)
