"""Pydantic models for User Personalization Engine (Week 7 · Day 1)."""

from __future__ import annotations

from pydantic import BaseModel, Field


LearningStyle = str  # video | reading | interactive | hands_on


class LearningPreferences(BaseModel):
    """Explicit and inferred learning preferences."""

    primary_style: LearningStyle = "interactive"
    style_scores: dict[str, float] = Field(
        default_factory=lambda: {
            "video": 0.25,
            "reading": 0.25,
            "interactive": 0.25,
            "hands_on": 0.25,
        }
    )
    preferred_session_minutes: int = 45
    preferred_study_time: str = "evening"  # morning | afternoon | evening
    content_formats: list[str] = Field(default_factory=list)
    updated_at: str | None = None


class InterviewHistoryEntry(BaseModel):
    session_id: str | None = None
    overall_score: float | None = None
    technical_score: float | None = None
    communication_score: float | None = None
    confidence_score: float | None = None
    interview_type: str | None = None
    completed_at: str | None = None


class UnifiedUserProfile(BaseModel):
    """Unified profile — weak/strong subjects, preferences, career, interviews."""

    user_id: str
    email: str | None = None
    full_name: str = "Student"
    subject_scores: dict[str, float] = Field(default_factory=dict)
    weak_subjects: list[str] = Field(default_factory=list)
    strong_subjects: list[str] = Field(default_factory=list)
    learning_preferences: LearningPreferences = Field(default_factory=LearningPreferences)
    career_goal: str | None = None
    interests: list[str] = Field(default_factory=list)
    interview_history: list[InterviewHistoryEntry] = Field(default_factory=list)
    interview_avg_score: float | None = None
    performance_score: float = 70.0
    study_hours_week: float = 10.0
    embedding_id: str | None = None
    profile_summary: str = ""
    created_at: str
    updated_at: str


class ProfileUpdateRequest(BaseModel):
    career_goal: str | None = None
    interests: list[str] | None = None
    subject_scores: dict[str, float] | None = None


class PreferencesUpdateRequest(BaseModel):
    primary_style: LearningStyle | None = None
    style_scores: dict[str, float] | None = None
    preferred_session_minutes: int | None = None
    preferred_study_time: str | None = None
    content_formats: list[str] | None = None


class PersonalizedResource(BaseModel):
    title: str
    description: str
    format: str
    style: LearningStyle
    subject: str
    priority: str = "medium"
    url_hint: str | None = None


class PersonalizedRecommendationsResponse(BaseModel):
    user_id: str
    learning_style: LearningStyle
    style_rationale: str
    weak_subjects: list[str]
    strong_subjects: list[str]
    resources: list[PersonalizedResource]
    study_actions: list[str]
    career_note: str | None = None
    used_embedding: bool = False


class SimilarUserMatch(BaseModel):
    user_id: str
    similarity: float
    shared_weak_subjects: list[str]
    learning_style: str


class ProfileBuildResponse(BaseModel):
    profile: UnifiedUserProfile
    recommendations: PersonalizedRecommendationsResponse
    embedding_updated: bool
