"""Automated weekly & monthly report generation (Week 7 · Day 4)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.learning_engine import LearningAnalyticsEngine
from app.memory.service import LongTermMemoryService
from app.models.reports import (
    MonthlyReportData,
    ReportSection,
    WeeklyReportData,
)
from app.personalization.profile_engine import UserProfileEngine
from app.personalization.recommender import PersonalizedRecommender
from app.reports.templates import monthly_markdown, weekly_markdown
from app.services.coach_service import CoachService


class ReportGenerator:
    @staticmethod
    async def weekly(user_id: str, db: AsyncSession | None = None) -> WeeklyReportData:
        profile = await UserProfileEngine.get_or_build(user_id, db)
        analytics = await LearningAnalyticsEngine.analyze(user_id, db)
        memory = LongTermMemoryService.get_progress(user_id, profile.subject_scores)
        coach = await CoachService.get_overview(db, target_career=profile.career_goal)
        pers = PersonalizedRecommender.recommend(profile)

        now = datetime.now(timezone.utc)
        period = now.strftime("Week of %b %d, %Y")

        learning = ReportSection(
            title="Learning Progress",
            content=(
                f"Overall performance **{analytics.learning_efficiency:.0f}%** efficient · "
                f"Productivity **{analytics.productivity_score:.0f}/100**. "
                f"{memory.narrative}"
            ),
            bullets=[
                f"Study streak insight: {analytics.patterns.productivity_pattern[:100]}…",
                f"Best study window: **{analytics.patterns.best_study_time}** "
                f"({', '.join(analytics.patterns.best_study_days)})",
            ]
            + [d.insight for d in memory.deltas[:2]],
        )

        from app.memory.store import get_memory_store

        mem = get_memory_store().get(user_id)
        recent_interviews = (mem.interview_scores[-3:] if mem else [])
        if recent_interviews:
            avg = sum(i.overall for i in recent_interviews) / len(recent_interviews)
            interview_content = f"Average mock interview score: **{avg:.0f}/100** across {len(recent_interviews)} recent sessions."
            interview_bullets = [
                f"Session {i.session_id or 'n/a'}: {i.overall:.0f}% ({i.interview_type or 'general'})"
                for i in recent_interviews
            ]
        else:
            interview_content = "No interview sessions recorded this period — schedule a mock interview."
            interview_bullets = ["Start a behavioral or technical mock interview this week"]

        interview = ReportSection(
            title="Interview Performance",
            content=interview_content,
            bullets=interview_bullets,
        )

        skill_bullets = [
            f"**{m.subject}**: {m.score}% ({m.mastery_level}, {m.trend})"
            for m in analytics.subject_mastery[:5]
        ]
        skill = ReportSection(
            title="Skill Growth",
            content="Subject mastery and month-over-month changes:",
            bullets=skill_bullets or [d.insight for d in memory.deltas[:4]],
        )

        rec_bullets = [f"**{r.title}** — {r.description[:80]}" for r in coach.recommendations[:3]]
        rec_bullets += [f"**{r.title}** ({r.format})" for r in pers.resources[:2]]
        recommendations = ReportSection(
            title="Recommendations",
            content=coach.weekly_report.next_week_plan[0] if coach.weekly_report.next_week_plan else "Keep your current study rhythm.",
            bullets=rec_bullets[:6],
        )

        data = WeeklyReportData(
            user_id=user_id,
            period_label=period,
            learning_progress=learning,
            interview_performance=interview,
            skill_growth=skill,
            recommendations=recommendations,
            markdown="",
            generated_at=now.isoformat(),
        )
        data.markdown = weekly_markdown(data)
        return data

    @staticmethod
    async def monthly(user_id: str, db: AsyncSession | None = None) -> MonthlyReportData:
        profile = await UserProfileEngine.get_or_build(user_id, db)
        analytics = await LearningAnalyticsEngine.analyze(user_id, db)
        coach = await CoachService.get_overview(db, target_career=profile.career_goal)
        memory = LongTermMemoryService.get_progress(user_id, profile.subject_scores)

        now = datetime.now(timezone.utc)
        period = now.strftime("%B %Y")

        career = ReportSection(
            title="Career Readiness",
            content=(
                f"Target role: **{coach.target_career}** · "
                f"Readiness **{coach.skill_gap.overall_readiness:.0f}%** · "
                f"{coach.profile_summary[:120]}…"
            ),
            bullets=[
                f"Top match rationale: {coach.recommendations[0].description[:90]}…"
                if coach.recommendations
                else "Explore career paths in the Career Agent",
                f"Missing skills: {', '.join(coach.skill_gap.missing_skills[:4])}",
            ],
        )

        stats = ReportSection(
            title="Learning Statistics",
            content=(
                f"Monthly efficiency **{analytics.learning_efficiency:.0f}%** · "
                f"Productivity **{analytics.productivity_score:.0f}/100** · "
                f"Burnout risk **{analytics.patterns.burnout_level}** ({analytics.patterns.burnout_risk:.0f}%)."
            ),
            bullets=[
                f"Performance trend: {analytics.summary}",
                f"Strong subjects: {', '.join(profile.strong_subjects) or 'building foundation'}",
                f"Weak subjects: {', '.join(profile.weak_subjects) or 'none critical'}",
                f"Study hours/week: ~{profile.study_hours_week:.0f}h",
            ],
        )

        improvements = ReportSection(
            title="Improvement Areas",
            content=memory.narrative,
            bullets=[i.description for i in analytics.insights if i.severity in ("warning", "info")][:4]
            + [d.insight for d in memory.deltas if d.delta < 0][:2]
            + coach.weekly_report.weaknesses[:2],
        )

        data = MonthlyReportData(
            user_id=user_id,
            period_label=period,
            career_readiness=career,
            learning_statistics=stats,
            improvement_areas=improvements,
            markdown="",
            generated_at=now.isoformat(),
        )
        data.markdown = monthly_markdown(data)
        return data
