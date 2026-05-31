"""Pydantic models for Automated Report Generator (Week 7 · Day 4)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    title: str
    content: str
    bullets: list[str] = Field(default_factory=list)


class WeeklyReportData(BaseModel):
    user_id: str
    period_label: str
    learning_progress: ReportSection
    interview_performance: ReportSection
    skill_growth: ReportSection
    recommendations: ReportSection
    markdown: str
    generated_at: str


class MonthlyReportData(BaseModel):
    user_id: str
    period_label: str
    career_readiness: ReportSection
    learning_statistics: ReportSection
    improvement_areas: ReportSection
    markdown: str
    generated_at: str


class ReportFileResponse(BaseModel):
    report_id: str
    report_type: str
    user_id: str
    markdown_path: str
    pdf_path: str | None = None
    generated_at: str


class EmailReportRequest(BaseModel):
    to_email: str | None = None
    report_type: str = "weekly"  # weekly | monthly


class EmailReportResponse(BaseModel):
    sent: bool
    message: str
    to_email: str | None = None
