"""Study tutor orchestration — daily recommendations & weak-subject analysis (Week 6 · Day 2)."""

from __future__ import annotations

from app.agents.study.curricula import LEARNING_RESOURCES
from app.agents.study.revision_planner import RevisionPlanner
from app.models.study_plan import PersonalizedRecommendationsRequest, SubjectScoreInput
from app.models.study_tutor import (
    DailyStudyRecommendation,
    DailyStudyRecommendationsResponse,
    WeakSubjectAnalysis,
)
from app.recommendation.engine import StudentProfile, get_recommendation_engine
from app.services.study_planner_service import StudyPlannerService


class StudyTutorService:
    @staticmethod
    def analyze_weak_subjects(
        subject_scores: dict[str, float] | None = None,
    ) -> list[WeakSubjectAnalysis]:
        engine = get_recommendation_engine()
        profile = engine.normalize_profile(
            StudentProfile(subject_scores=subject_scores or engine.default_subject_scores())
        )
        weak = engine.weak_subjects(profile)
        out: list[WeakSubjectAnalysis] = []
        for subject, score in weak:
            topics = [engine._topic_for_subject(subject, score)]
            priority = "high" if score < 60 else "medium" if score < 70 else "low"
            minutes = 90 if priority == "high" else 60 if priority == "medium" else 45
            out.append(
                WeakSubjectAnalysis(
                    subject=subject,
                    score=score,
                    priority=priority,
                    suggested_topics=topics,
                    resources=LEARNING_RESOURCES.get(subject, [])[:3],
                    daily_minutes=minutes,
                )
            )
        return out

    @staticmethod
    def daily_recommendations(
        subject_scores: dict[str, float] | None = None,
        user_id: str | None = None,
    ) -> DailyStudyRecommendationsResponse:
        engine = get_recommendation_engine()
        pers = None
        if user_id:
            from app.personalization.store import get_profile_store
            from app.personalization.recommender import PersonalizedRecommender

            profile = get_profile_store().get(user_id)
            if profile:
                subject_scores = profile.subject_scores or subject_scores
                pers = PersonalizedRecommender.recommend(profile)

        scores = subject_scores or engine.default_subject_scores()
        req = PersonalizedRecommendationsRequest(
            subject_scores=[SubjectScoreInput(subject=s, score=sc) for s, sc in scores.items()]
        )
        plan = StudyPlannerService.daily_study_planner(req)
        recs = StudyPlannerService.generate_recommendations(req)
        weak = StudyTutorService.analyze_weak_subjects(scores)

        recommendations: list[DailyStudyRecommendation] = []
        for slot in plan.timetable[:4]:
            recommendations.append(
                DailyStudyRecommendation(
                    title=slot.task,
                    description=f"{slot.topic} — {slot.priority} priority",
                    subject=slot.subject,
                    priority=slot.priority,
                    estimated_minutes=int(slot.duration_hours * 60),
                )
            )
        for item in recs.recommendations[:2]:
            recommendations.append(
                DailyStudyRecommendation(
                    title=item.title,
                    description=item.description,
                    subject=item.topic or "General",
                    priority=item.priority,
                    estimated_minutes=45,
                )
            )

        if pers:
            for res in pers.resources[:2]:
                recommendations.append(
                    DailyStudyRecommendation(
                        title=res.title,
                        description=res.description,
                        subject=res.subject,
                        priority=res.priority,
                        estimated_minutes=45,
                    )
                )

        focus = [f"{fa.subject}: {fa.topic}" for fa in plan.focus_areas[:3]]
        streak_tip = (
            pers.style_rationale
            if pers
            else "Students who study 30+ minutes daily for 14 days see ~12% score improvement "
            "in collaborative filter data."
        )

        return DailyStudyRecommendationsResponse(
            summary=plan.summary,
            weak_subjects=weak,
            recommendations=recommendations,
            focus_areas=focus,
            study_streak_tip=streak_tip,
        )

    @staticmethod
    def format_daily_markdown(data: DailyStudyRecommendationsResponse) -> str:
        lines = [f"**Today's study recommendations**\n\n{data.summary}", ""]
        if data.weak_subjects:
            lines.append("**Weak subjects**")
            for w in data.weak_subjects:
                res = w.resources[0] if w.resources else "practice problems"
                lines.append(
                    f"• **{w.subject}** ({w.score:.0f}%) — {w.daily_minutes} min/day · _{res}_"
                )
            lines.append("")
        lines.append("**Today's tasks**")
        for r in data.recommendations[:5]:
            lines.append(f"• [{r.priority}] **{r.subject}**: {r.title} (~{r.estimated_minutes} min)")
        lines.append("")
        lines.append(f"_{data.study_streak_tip}_")
        return "\n".join(lines)

    @staticmethod
    def format_weak_subjects_markdown(weak: list[WeakSubjectAnalysis]) -> str:
        if not weak:
            return "No critical weak subjects detected — maintain your current study rhythm."
        lines = ["**Weak subject analysis**\n"]
        for w in weak:
            topics = ", ".join(w.suggested_topics)
            resources = "\n".join(f"    - {r}" for r in w.resources[:2])
            lines.append(
                f"**{w.subject}** ({w.score:.0f}%) — {w.priority} priority\n"
                f"  Focus: {topics}\n"
                f"  Daily: {w.daily_minutes} min\n"
                f"  Resources:\n{resources}\n"
            )
        return "\n".join(lines)

    @staticmethod
    def format_revision_markdown(message: str) -> str:
        from app.agents.study.revision_planner import parse_revision_request

        subject, days = parse_revision_request(message)
        plan = RevisionPlanner.build(
            RevisionPlanRequest(exam_subject=subject, days_until_exam=days)
        )
        return RevisionPlanner.to_markdown(plan)
