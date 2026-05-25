from app.recommendation.engine import RecommendationEngine, StudentProfile, get_recommendation_engine
from app.models.recommendation import RecommendationItem
from app.models.study_plan import (
    DailyStudyPlannerResponse,
    FocusArea,
    PersonalizedRecommendationsRequest,
    PersonalizedRecommendationsResponse,
    SubjectScoreInput,
    TimetableSlot,
)


class StudyPlannerService:
    @staticmethod
    def _profile_from_request(req: PersonalizedRecommendationsRequest | None) -> StudentProfile:
        engine = get_recommendation_engine()
        if req is None:
            return engine.normalize_profile(None)

        scores: dict[str, float] = {}
        if req.subject_scores:
            scores = {s.subject: s.score for s in req.subject_scores}

        profile = StudentProfile(
            study_hours=req.study_hours,
            attendance_pct=req.attendance_pct,
            sleep_hours=req.sleep_hours,
            past_failures=req.past_failures,
            subject_scores=scores,
            predicted_score=req.predicted_score,
            risk_level=req.risk_level,
        )
        return engine.normalize_profile(profile)

    @staticmethod
    def generate_recommendations(
        req: PersonalizedRecommendationsRequest | None = None,
    ) -> PersonalizedRecommendationsResponse:
        engine = get_recommendation_engine()
        profile = StudyPlannerService._profile_from_request(req)

        rule_recs = engine.rule_based_recommendations(profile)
        cf_insights = engine.collaborative_suggestions(profile)
        items = [
            RecommendationItem(**d)
            for d in engine.to_recommendation_items(rule_recs)
        ]

        weak = [
            SubjectScoreInput(subject=s, score=sc)
            for s, sc in engine.weak_subjects(profile)
        ]
        order = engine.revision_order(profile)

        focus_msg = StudyPlannerService._focus_message(profile, weak, order)

        return PersonalizedRecommendationsResponse(
            recommendations=items,
            weak_subjects=weak,
            revision_order=order,
            collaborative_insights=cf_insights,
            focus_message=focus_msg,
        )

    @staticmethod
    def daily_study_planner(
        req: PersonalizedRecommendationsRequest | None = None,
    ) -> DailyStudyPlannerResponse:
        engine = get_recommendation_engine()
        profile = StudyPlannerService._profile_from_request(req)

        plan = engine.build_study_plan(profile)
        rule_recs = engine.rule_based_recommendations(profile)
        items = [
            RecommendationItem(**d)
            for d in engine.to_recommendation_items(rule_recs)
        ]

        return DailyStudyPlannerResponse(
            revision_priority=plan["revision_priority"],
            focus_areas=[FocusArea(**f) for f in plan["focus_areas"]],
            weekly_study_hours=plan["weekly_study_hours"],
            timetable=[TimetableSlot(**t) for t in plan["timetable"]],
            collaborative_insights=plan["collaborative_insights"],
            summary=plan["summary"],
            recommendations=items,
        )

    @staticmethod
    def _focus_message(
        profile: StudentProfile,
        weak: list[SubjectScoreInput],
        order: list[str],
    ) -> str:
        engine = get_recommendation_engine()
        if weak:
            w = weak[0]
            topic = engine._topic_for_subject(w.subject, w.score)
            if w.subject == "Mathematics" and w.score < 70:
                return f"Focus on {topic} revision this week — math at {w.score:.0f}%."
            return f"Priority: {w.subject} ({topic}) — score {w.score:.0f}%."
        if profile.attendance_pct < 75:
            return "Raise attendance first — it unlocks better outcomes across all subjects."
        return "Balanced week — maintain strengths and light review on all topics."
