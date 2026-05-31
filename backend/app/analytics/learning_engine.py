"""AI Learning Analytics engine — insights, trends, productivity (Week 7 · Day 3)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.patterns import PatternDetector
from app.analytics.service import compute_risk_meter
from app.memory.service import LongTermMemoryService
from app.models.common import ChartPoint
from app.models.learning_analytics import (
    LearningAnalyticsDashboard,
    LearningInsight,
    SubjectMastery,
)
from app.personalization.profile_engine import UserProfileEngine
from app.services.dashboard_service import DashboardService

MASTERY_THRESHOLDS = [
    (90, "mastered"),
    (75, "proficient"),
    (60, "developing"),
    (0, "beginner"),
]


class LearningAnalyticsEngine:
    @staticmethod
    async def analyze(user_id: str, db: AsyncSession | None = None) -> LearningAnalyticsDashboard:
        profile = await UserProfileEngine.get_or_build(user_id, db)
        dashboard = await DashboardService.get_dashboard(db)
        memory_progress = LongTermMemoryService.get_progress(user_id, profile.subject_scores)
        analytics = dashboard.analytics

        delta_map = {d.subject: d for d in memory_progress.deltas}
        subject_mastery = LearningAnalyticsEngine._subject_mastery(
            profile.subject_scores, delta_map
        )

        risk = compute_risk_meter(
            dashboard.performance_score,
            study_hours_week=dashboard.study_hours_week,
            attendance_pct=78.0,
            sleep_hours=6.8,
        )

        patterns = PatternDetector.detect(
            subject_scores=profile.subject_scores,
            weak_subjects=profile.weak_subjects,
            strong_subjects=profile.strong_subjects,
            preferred_study_time=profile.learning_preferences.preferred_study_time,
            study_hours_by_day=dashboard.study_hours_by_day,
            study_hours_week=dashboard.study_hours_week,
            study_streak=analytics.cards.study_streak_days,
            burnout_risk=risk.burnout_risk,
        )

        efficiency = LearningAnalyticsEngine._learning_efficiency(
            dashboard.performance_score,
            dashboard.study_hours_week,
            len(profile.weak_subjects),
            analytics.cards.study_streak_days,
        )
        productivity = LearningAnalyticsEngine._productivity_score(
            dashboard.study_hours_week,
            analytics.cards.study_streak_days,
            dashboard.performance_score,
            risk.burnout_risk,
        )

        insights = LearningAnalyticsEngine._generate_insights(
            patterns, efficiency, productivity, subject_mastery, memory_progress.deltas
        )

        weekly_growth = list(dashboard.performance_trend)
        if memory_progress.deltas:
            growth_val = sum(d.delta for d in memory_progress.deltas[:3]) / max(
                1, min(3, len(memory_progress.deltas))
            )
            weekly_growth = weekly_growth + [
                ChartPoint(
                    label="Now",
                    value=round(weekly_growth[-1].value + growth_val, 1) if weekly_growth else 70,
                )
            ]

        summary = LearningAnalyticsEngine._summary(
            efficiency, productivity, patterns, analytics.cards.performance_trend_delta
        )

        return LearningAnalyticsDashboard(
            user_id=user_id,
            learning_efficiency=efficiency,
            productivity_score=productivity,
            weekly_growth=weekly_growth,
            subject_mastery=subject_mastery,
            progress_trends=analytics.weekly_progress,
            study_hours_by_day=dashboard.study_hours_by_day,
            patterns=patterns,
            insights=insights,
            risk_meter=risk,
            summary=summary,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _subject_mastery(scores: dict[str, float], deltas: dict) -> list[SubjectMastery]:
        items: list[SubjectMastery] = []
        for subject, score in sorted(scores.items(), key=lambda x: -x[1]):
            level = "beginner"
            for threshold, label in MASTERY_THRESHOLDS:
                if score >= threshold:
                    level = label
                    break
            delta = deltas[subject].delta if subject in deltas else 0.0
            trend = "up" if delta > 2 else "down" if delta < -2 else "stable"
            items.append(
                SubjectMastery(
                    subject=subject,
                    score=round(score, 1),
                    mastery_level=level,
                    trend=trend,
                    delta=round(delta, 1),
                )
            )
        return items

    @staticmethod
    def _learning_efficiency(
        performance: float,
        hours_week: float,
        weak_count: int,
        streak: int,
    ) -> float:
        hours_factor = min(100, (hours_week / 35) * 100) * 0.25
        perf_factor = performance * 0.45
        weak_penalty = max(0, weak_count * 5)
        streak_bonus = min(15, streak * 0.8)
        raw = perf_factor + hours_factor + streak_bonus - weak_penalty
        return round(max(0, min(100, raw)), 1)

    @staticmethod
    def _productivity_score(
        hours_week: float,
        streak: int,
        performance: float,
        burnout_risk: float,
    ) -> float:
        consistency = min(40, streak * 2.5)
        output = min(35, (hours_week / 30) * 35)
        quality = performance * 0.25
        burnout_penalty = burnout_risk * 0.2
        raw = consistency + output + quality - burnout_penalty
        return round(max(0, min(100, raw)), 1)

    @staticmethod
    def _generate_insights(patterns, efficiency, productivity, mastery, deltas) -> list[LearningInsight]:
        insights: list[LearningInsight] = []

        insights.append(
            LearningInsight(
                category="study_time",
                title=f"Best study time: {patterns.best_study_time.title()}",
                description=(
                    f"Your peak study days are **{', '.join(patterns.best_study_days)}**. "
                    f"Schedule deep work during **{patterns.best_study_time}** sessions for best retention."
                ),
                severity="info",
            )
        )

        insights.append(
            LearningInsight(
                category="productivity",
                title=f"Productivity score: {productivity:.0f}/100",
                description=patterns.productivity_pattern,
                severity="success" if productivity >= 70 else "info",
            )
        )

        if patterns.weak_learning_areas:
            weak = ", ".join(patterns.weak_learning_areas[:3])
            insights.append(
                LearningInsight(
                    category="weakness",
                    title="Weak learning areas detected",
                    description=f"Focus revision on **{weak}** — these subjects drag down overall efficiency ({efficiency:.0f}%).",
                    severity="warning",
                )
            )

        burnout_sev = "warning" if patterns.burnout_level != "low" else "success"
        insights.append(
            LearningInsight(
                category="burnout",
                title=f"Burnout risk: {patterns.burnout_level}",
                description=(
                    f"Burnout index at **{patterns.burnout_risk:.0f}%**. "
                    + (
                        "Take rest days and protect sleep — high load detected."
                        if patterns.burnout_level != "low"
                        else "Healthy balance — keep your current rhythm."
                    )
                ),
                severity=burnout_sev,
            )
        )

        improved = [m for m in mastery if m.trend == "up"]
        if improved:
            insights.append(
                LearningInsight(
                    category="growth",
                    title=f"Weekly growth in {improved[0].subject}",
                    description=f"**{improved[0].subject}** trending up (+{improved[0].delta:.0f} pts) — {improved[0].mastery_level} level.",
                    severity="success",
                )
            )
        elif deltas:
            top = deltas[0]
            if top.delta_pct >= 5:
                insights.append(
                    LearningInsight(
                        category="growth",
                        title=f"Progress in {top.subject}",
                        description=top.insight,
                        severity="success",
                    )
                )

        return insights[:6]

    @staticmethod
    def _summary(efficiency: float, productivity: float, patterns, trend_delta: float) -> str:
        trend_word = "up" if trend_delta >= 0 else "down"
        return (
            f"Learning efficiency **{efficiency:.0f}%** · Productivity **{productivity:.0f}/100**. "
            f"Best study window: **{patterns.best_study_time}**. "
            f"Weekly performance trending **{trend_word}** ({trend_delta:+.0f} pts)."
        )
