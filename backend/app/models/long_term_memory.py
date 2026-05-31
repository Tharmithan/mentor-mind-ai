"""Pydantic models for Long-Term Memory System (Week 7 · Day 2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConversationMemoryEntry(BaseModel):
    session_id: str
    source: str = "agent"  # agent | chat
    summary: str
    topics: list[str] = Field(default_factory=list)
    agent: str | None = None
    recorded_at: str


class StudyPlanMemoryEntry(BaseModel):
    plan_id: str | None = None
    subject: str
    summary: str
    recorded_at: str


class InterviewScoreMemoryEntry(BaseModel):
    session_id: str | None = None
    overall: float
    technical: float | None = None
    communication: float | None = None
    interview_type: str | None = None
    recorded_at: str


class CareerGoalMemoryEntry(BaseModel):
    goal: str
    recorded_at: str
    active: bool = True


class SubjectSnapshot(BaseModel):
    month: str
    label: str
    scores: dict[str, float]
    recorded_at: str


class LongTermMemory(BaseModel):
    user_id: str
    conversations: list[ConversationMemoryEntry] = Field(default_factory=list)
    study_plans: list[StudyPlanMemoryEntry] = Field(default_factory=list)
    interview_scores: list[InterviewScoreMemoryEntry] = Field(default_factory=list)
    career_goals: list[CareerGoalMemoryEntry] = Field(default_factory=list)
    subject_snapshots: list[SubjectSnapshot] = Field(default_factory=list)
    created_at: str
    updated_at: str


class ProgressDelta(BaseModel):
    subject: str
    previous_score: float
    current_score: float
    delta: float
    delta_pct: float
    period_label: str
    insight: str


class MemoryContextResponse(BaseModel):
    user_id: str
    summary: str
    progress_insights: list[str]
    progress_deltas: list[ProgressDelta]
    relevant_conversations: list[ConversationMemoryEntry]
    active_career_goal: str | None = None
    recent_interview_avg: float | None = None
    retrieved_at: str


class MemoryProgressResponse(BaseModel):
    user_id: str
    deltas: list[ProgressDelta]
    narrative: str
    snapshots_count: int
    month_comparison: str


class RecordMemoryRequest(BaseModel):
    kind: str  # conversation | study_plan | interview | career_goal | snapshot
    payload: dict
