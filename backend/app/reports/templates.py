"""Markdown report templates (Week 7 · Day 4)."""

from __future__ import annotations

from app.models.reports import MonthlyReportData, ReportSection, WeeklyReportData


def _section_md(section: ReportSection) -> str:
    lines = [f"## {section.title}", "", section.content, ""]
    for b in section.bullets:
        lines.append(f"- {b}")
    lines.append("")
    return "\n".join(lines)


def weekly_markdown(data: WeeklyReportData) -> str:
    lines = [
        f"# MentorMind AI — Weekly Learning Report",
        f"**Period:** {data.period_label}  ",
        f"**Student ID:** {data.user_id}  ",
        f"**Generated:** {data.generated_at}",
        "",
        "---",
        "",
        _section_md(data.learning_progress),
        _section_md(data.interview_performance),
        _section_md(data.skill_growth),
        _section_md(data.recommendations),
        "---",
        "",
        "*Generated automatically by MentorMind AI Report Engine*",
    ]
    return "\n".join(lines)


def monthly_markdown(data: MonthlyReportData) -> str:
    lines = [
        f"# MentorMind AI — Monthly Career & Learning Report",
        f"**Period:** {data.period_label}  ",
        f"**Student ID:** {data.user_id}  ",
        f"**Generated:** {data.generated_at}",
        "",
        "---",
        "",
        _section_md(data.career_readiness),
        _section_md(data.learning_statistics),
        _section_md(data.improvement_areas),
        "---",
        "",
        "*Generated automatically by MentorMind AI Report Engine*",
    ]
    return "\n".join(lines)
