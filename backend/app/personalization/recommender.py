"""Style-aware personalized recommendations (Week 7 · Day 1)."""

from __future__ import annotations

from app.agents.study.curricula import LEARNING_RESOURCES
from app.models.personalization import (
    PersonalizedRecommendationsResponse,
    PersonalizedResource,
    UnifiedUserProfile,
)
from app.personalization.preferences import STYLE_DEFAULT_FORMATS, LearningPreferenceTracker
from app.recommendation.engine import get_recommendation_engine

# Map resource strings to learning styles via keyword heuristics
_STYLE_HINTS: dict[str, list[str]] = {
    "video": ["youtube", "3blue1brown", "video", "coursera", "khan", "visualgo", "fast.ai"],
    "reading": ["documentation", "docs", "openstax", "textbook", "notes", "mdn", "guide", "clrs"],
    "interactive": ["leetcode", "neetcode", "quiz", "duolingo", "exercism", "kaggle learn", "flashcard"],
    "hands_on": ["kaggle", "project", "build", "github", "fastapi", "real python"],
}


class PersonalizedRecommender:
    @staticmethod
    def recommend(profile: UnifiedUserProfile) -> PersonalizedRecommendationsResponse:
        style = profile.learning_preferences.primary_style
        engine = get_recommendation_engine()
        resources: list[PersonalizedResource] = []

        # Style-native formats first (User A vs User B example)
        for fmt in STYLE_DEFAULT_FORMATS.get(style, [])[:2]:
            subject = profile.weak_subjects[0] if profile.weak_subjects else "Programming"
            resources.append(
                PersonalizedResource(
                    title=fmt,
                    description=f"Recommended {fmt.lower()} for {subject} — matches your {style} learning style.",
                    format=fmt,
                    style=style,
                    subject=subject,
                    priority="high",
                )
            )

        # Subject-specific resources filtered by style
        subjects = profile.weak_subjects[:2] or profile.strong_subjects[:1] or ["Programming"]
        for subject in subjects:
            for raw in LEARNING_RESOURCES.get(subject, LEARNING_RESOURCES.get("Programming", [])):
                res_style = PersonalizedRecommender._classify_resource(raw)
                if res_style == style or style == "interactive":
                    score = profile.subject_scores.get(subject, 70)
                    priority = "high" if score < 65 else "medium"
                    resources.append(
                        PersonalizedResource(
                            title=raw.split("—")[0].strip() if "—" in raw else raw[:60],
                            description=raw,
                            format=res_style,
                            style=res_style,
                            subject=subject,
                            priority=priority,
                            url_hint=_url_hint(raw),
                        )
                    )
                if len(resources) >= 8:
                    break
            if len(resources) >= 8:
                break

        # Fill if sparse
        if len(resources) < 4:
            for fmt in STYLE_DEFAULT_FORMATS.get(style, []):
                resources.append(
                    PersonalizedResource(
                        title=fmt,
                        description=f"Core {style} resource for your study plan.",
                        format=fmt,
                        style=style,
                        subject=subjects[0],
                        priority="medium",
                    )
                )

        study_actions = PersonalizedRecommender._study_actions(profile)
        career_note = None
        if profile.career_goal:
            career_note = f"Align {style} study with your goal: **{profile.career_goal}**."

        try:
            from app.monitoring.improvement import ImprovementLoop

            resources = ImprovementLoop.filter_recommendations(profile.user_id, resources)
            loop = ImprovementLoop.analyze(profile.user_id)
            if loop.improved_recommendation_note:
                career_note = (career_note or "") + " " + loop.improved_recommendation_note
        except Exception:
            pass

        return PersonalizedRecommendationsResponse(
            user_id=profile.user_id,
            learning_style=style,
            style_rationale=LearningPreferenceTracker.rationale(style),
            weak_subjects=profile.weak_subjects,
            strong_subjects=profile.strong_subjects,
            resources=resources[:8],
            study_actions=study_actions,
            career_note=career_note,
            used_embedding=profile.embedding_id is not None,
        )

    @staticmethod
    def _classify_resource(text: str) -> str:
        lower = text.lower()
        scores = {style: 0 for style in _STYLE_HINTS}
        for style, hints in _STYLE_HINTS.items():
            for h in hints:
                if h in lower:
                    scores[style] += 1
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        return best if scores[best] > 0 else "reading"

    @staticmethod
    def _study_actions(profile: UnifiedUserProfile) -> list[str]:
        actions: list[str] = []
        style = profile.learning_preferences.primary_style
        mins = profile.learning_preferences.preferred_session_minutes

        if profile.weak_subjects:
            w = profile.weak_subjects[0]
            sc = profile.subject_scores.get(w, 0)
            topic = get_recommendation_engine()._topic_for_subject(w, sc)
            if style == "video":
                actions.append(f"Watch 2 {w} tutorials ({mins} min each) on {topic}")
            elif style == "reading":
                actions.append(f"Read docs/chapter on {topic} for {w} ({mins} min)")
            elif style == "interactive":
                actions.append(f"Complete 15 {w} quiz questions on {topic}")
            else:
                actions.append(f"Build a small {w} project applying {topic}")

        if profile.interview_avg_score and profile.interview_avg_score < 75:
            actions.append("Schedule a mock interview to improve confidence")
        elif not profile.interview_history:
            actions.append("Try your first mock interview this week")

        if profile.strong_subjects:
            actions.append(f"Maintain {profile.strong_subjects[0]} with light weekly review")

        return actions[:4]


def _url_hint(resource: str) -> str | None:
    lower = resource.lower()
    if "youtube" in lower or "3blue1brown" in lower:
        return "https://youtube.com"
    if "khan" in lower:
        return "https://khanacademy.org"
    if "leetcode" in lower or "neetcode" in lower:
        return "https://leetcode.com"
    if "kaggle" in lower:
        return "https://kaggle.com/learn"
    return None
