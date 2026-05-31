"""Pydantic models for Resume Analyzer (Week 6 · Day 4)."""

from pydantic import BaseModel, Field


class ResumeSection(BaseModel):
    name: str
    content: str
    line_count: int = 0


class ATSCheckItem(BaseModel):
    category: str
    label: str
    passed: bool
    score: float = Field(ge=0, le=10)
    detail: str


class MissingSkill(BaseModel):
    skill: str
    importance: str
    suggestion: str


class WeakBullet(BaseModel):
    text: str
    issue: str
    suggestion: str


class ResumeFeedbackItem(BaseModel):
    category: str
    priority: str
    message: str


class ResumeAnalysisResponse(BaseModel):
    analysis_id: str
    filename: str | None = None
    word_count: int
    page_estimate: int
    sections: list[ResumeSection]
    ats_score: float = Field(ge=0, le=100)
    ats_grade: str
    ats_checks: list[ATSCheckItem]
    missing_skills: list[MissingSkill]
    weak_bullets: list[WeakBullet]
    formatting_issues: list[str]
    feedback: list[ResumeFeedbackItem]
    summary: str
    headline: str
    used_llm: bool = False


class ResumeTextAnalyzeRequest(BaseModel):
    text: str = Field(min_length=50)
    target_role: str | None = None
