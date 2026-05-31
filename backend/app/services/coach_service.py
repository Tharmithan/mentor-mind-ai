"""AI Coach Dashboard — aggregates scores, charts, skill gaps, weekly reports (Week 6 · Day 7)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.career.profile_builder import ProfileBuilder, resolve_career_id
from app.agents.career.recommendation_engine import CareerRecommendationEngine
from app.agents.career.skill_gap import SkillGapAnalyzer
from app.agents.study.goal_tracker import GoalTracker
from app.models.career import CareerAnalysisRequest
from app.models.coach import (
    CoachCharts,
    CoachOverviewResponse,
    CoachRecommendation,
    CoachScoreCard,
    SkillGapOverview,
    WeeklyProgressReport,
)
from app.models.common import ChartPoint
from app.services.dashboard_service import DashboardService

INTERVIEW_DIR = Path(__file__).resolve().parents[2] / "uploads" / "interview_sessions"
RESUMES_DIR = Path(__file__).resolve().parents[2] / "uploads" / "resumes"

_DEMO_SUBJECT_SCORES = {
    "Mathematics": 88,
    "Programming": 78,
    "Data Structures": 62,
    "Portuguese": 75,
}

_DEMO_INTERVIEW_TREND = [58, 64, 68, 72, 76]
_DEMO_READINESS_TREND = [52, 58, 63, 68, 72]


class CoachService:
    @staticmethod
    async def get_overview(
        db: AsyncSession | None,
        target_career: str | None = None,
        session_id: str | None = None,
        interview_session_id: str | None = None,
    ) -> CoachOverviewResponse:
        dashboard = await DashboardService.get_dashboard(db)
        career_id = resolve_career_id(target_career) or "ai_engineer"

        profile = ProfileBuilder.build(
            message=target_career,
            subject_scores=_DEMO_SUBJECT_SCORES,
            interview_session_id=interview_session_id,
        )
        skill_gaps = SkillGapAnalyzer.analyze(profile, career_id)

        career_req = CareerAnalysisRequest(
            target_career=target_career or skill_gaps.target_career,
            subject_scores=_DEMO_SUBJECT_SCORES,
            interview_session_id=interview_session_id,
        )
        career_rec = await CareerRecommendationEngine.from_request(career_req, target_career)

        learning_score = dashboard.performance_score
        interview_score = profile.interview_overall or _avg_interview_score() or 72.0
        career_readiness = skill_gaps.overall_readiness
        resume_score = _latest_resume_score() or 68.0

        recommendations = _build_recommendations(
            career_rec, skill_gaps, dashboard, learning_score, interview_score
        )

        scores = [
            CoachScoreCard(
                label="Learning Score",
                score=round(learning_score, 1),
                delta=dashboard.analytics.cards.performance_trend_delta,
                trend="up" if dashboard.analytics.cards.performance_trend_delta >= 0 else "down",
                subtitle=f"{dashboard.study_hours_week}h studied this week",
            ),
            CoachScoreCard(
                label="Interview Score",
                score=round(interview_score, 1),
                delta=round(_DEMO_INTERVIEW_TREND[-1] - _DEMO_INTERVIEW_TREND[-2], 1),
                trend="up",
                subtitle="Based on mock interview sessions",
            ),
            CoachScoreCard(
                label="Career Readiness",
                score=round(career_readiness, 1),
                delta=round(_DEMO_READINESS_TREND[-1] - _DEMO_READINESS_TREND[-2], 1),
                trend="up",
                subtitle=f"Target: {skill_gaps.target_career}",
            ),
            CoachScoreCard(
                label="Resume Score",
                score=round(resume_score, 1),
                delta=4.0,
                trend="up",
                subtitle="ATS compatibility estimate",
            ),
            CoachScoreCard(
                label="AI Recommendations",
                score=float(len(recommendations)),
                delta=0,
                trend="neutral",
                subtitle=f"{len([r for r in recommendations if r.priority == 'high'])} high priority",
            ),
        ]

        current_skills = [
            s.replace("_", " ").title()
            for s, level in sorted(profile.skills.items(), key=lambda x: -x[1])[:6]
            if level >= 55
        ]
        missing_skills = [g.skill for g in skill_gaps.gaps[:6]]

        skill_gap = SkillGapOverview(
            target_career=skill_gaps.target_career,
            current_skills=current_skills or ["Python", "SQL"],
            missing_skills=missing_skills or ["Deep Learning", "MLOps", "LLMs"],
            overall_readiness=skill_gaps.overall_readiness,
            gaps=skill_gaps.gaps,
        )

        skill_growth = _build_skill_growth(profile.skills, career_id)
        charts = CoachCharts(
            skill_growth=skill_growth,
            learning_progress=dashboard.performance_trend,
            interview_improvement=[
                ChartPoint(label=f"W{i + 1}", value=float(v))
                for i, v in enumerate(_DEMO_INTERVIEW_TREND)
            ],
            career_readiness_trend=[
                ChartPoint(label=f"W{i + 1}", value=float(v))
                for i, v in enumerate(_DEMO_READINESS_TREND)
            ],
        )

        weekly_report = _generate_weekly_report(
            dashboard, skill_gaps, session_id, learning_score, interview_score
        )

        return CoachOverviewResponse(
            scores=scores,
            charts=charts,
            skill_gap=skill_gap,
            recommendations=recommendations,
            weekly_report=weekly_report,
            target_career=skill_gaps.target_career,
            profile_summary=career_rec.profile_summary,
        )


def _avg_interview_score() -> float | None:
    if not INTERVIEW_DIR.exists():
        return None
    totals: list[float] = []
    for path in sorted(INTERVIEW_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            summary = data.get("summary") or {}
            overall = summary.get("overall_score") or summary.get("overall")
            if overall is not None:
                totals.append(float(overall))
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            continue
    return round(sum(totals) / len(totals), 1) if totals else None


def _latest_resume_score() -> float | None:
    if not RESUMES_DIR.exists():
        return None
    paths = sorted(RESUMES_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths[:3]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            score = data.get("ats_score")
            if score is not None:
                return float(score)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            continue
    return None


def _build_skill_growth(skills: dict[str, float], career_id: str) -> list[ChartPoint]:
    """Average skill level growth over 5 weeks."""
    avg = sum(skills.values()) / len(skills) if skills else 62.0
    base = round(avg * 0.82, 1)
    step = (avg - base) / 4
    return [
        ChartPoint(label=f"W{i + 1}", value=round(base + step * i, 1))
        for i in range(5)
    ]


def _build_recommendations(career_rec, skill_gaps, dashboard, learning_score, interview_score):
    recs: list[CoachRecommendation] = []

    for gap in skill_gaps.gaps[:2]:
        recs.append(
            CoachRecommendation(
                id=uuid.uuid4().hex[:8],
                title=f"Close gap: {gap.skill}",
                description=gap.learning_actions[0] if gap.learning_actions else f"Improve {gap.skill}",
                agent="career",
                priority=gap.priority,
                action_path="/planner",
            )
        )

    if learning_score < 75:
        weak = dashboard.weak_subjects[0].subject if dashboard.weak_subjects else "Data Structures"
        recs.append(
            CoachRecommendation(
                id=uuid.uuid4().hex[:8],
                title=f"Strengthen {weak}",
                description=f"Your {weak} score is below target — schedule focused revision.",
                agent="study",
                priority="high",
                action_path="/assistant",
            )
        )

    if interview_score < 80:
        recs.append(
            CoachRecommendation(
                id=uuid.uuid4().hex[:8],
                title="Practice mock interviews",
                description="Run a technical mock interview to boost confidence and scores.",
                agent="interview",
                priority="medium",
                action_path="/interview",
            )
        )

    recs.append(
        CoachRecommendation(
            id=uuid.uuid4().hex[:8],
            title=f"Path to {career_rec.top_career.title}",
            description=career_rec.top_career.rationale[:120],
            agent="career",
            priority="medium",
            action_path="/planner",
        )
    )

    recs.append(
        CoachRecommendation(
            id=uuid.uuid4().hex[:8],
            title="Polish resume for ATS",
            description="Upload your resume for AI feedback and missing keyword detection.",
            agent="resume",
            priority="medium",
            action_path="/resume",
        )
    )

    return recs[:5]


def _generate_weekly_report(dashboard, skill_gaps, session_id, learning_score, interview_score):
    goals = GoalTracker().list_goals(session_id) if session_id else []
    completed_goals = [g for g in goals if g.progress_pct >= 100]

    achievements = [
        f"Learning score reached **{learning_score:.0f}%** (+{dashboard.analytics.cards.performance_trend_delta:.0f} this month)",
        f"Studied **{dashboard.study_hours_week:.0f} hours** this week",
    ]
    if completed_goals:
        achievements.append(f"Completed goal: **{completed_goals[0].title}**")
    else:
        achievements.append(f"Career match identified: **{skill_gaps.target_career}**")

    weaknesses = []
    if dashboard.weak_subjects:
        w = dashboard.weak_subjects[0]
        weaknesses.append(f"**{w.subject}** at {w.score:.0f}% — needs focused practice")
    high_gaps = [g for g in skill_gaps.gaps if g.priority == "high"]
    for g in high_gaps[:2]:
        weaknesses.append(f"Missing **{g.skill}** ({g.gap:.0f} point gap)")
    if interview_score < 75:
        weaknesses.append("Interview confidence below target — more mock sessions recommended")
    if not weaknesses:
        weaknesses.append("Keep momentum — no critical gaps this week")

    next_week = []
    if skill_gaps.gaps:
        top = skill_gaps.gaps[0]
        next_week.append(f"Study **{top.skill}** — {top.learning_actions[0] if top.learning_actions else '2h/day'}")
    next_week.append("Complete 2 mock interview sessions (technical + behavioral)")
    next_week.append("Update resume with one quantified project bullet")
    if dashboard.recommendations:
        r = dashboard.recommendations[0]
        next_week.append(f"Follow AI suggestion: **{r.title}**")

    return WeeklyProgressReport(
        week_label=datetime.now(timezone.utc).strftime("Week of %b %d, %Y"),
        achievements=achievements,
        weaknesses=weaknesses,
        next_week_plan=next_week,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
