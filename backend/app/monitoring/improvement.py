"""Continuous improvement loop from feedback (Week 7 · Day 6)."""

from __future__ import annotations

from app.models.monitoring import ImprovementInsight, ImprovementLoopResponse
from app.monitoring.collector import FeedbackCollector
from app.monitoring.satisfaction import SatisfactionTracker


class ImprovementLoop:
    @staticmethod
    def analyze(user_id: str) -> ImprovementLoopResponse:
        satisfaction = SatisfactionTracker.summarize(user_id)
        downranked = FeedbackCollector.negative_targets(user_id)
        rec_bad = FeedbackCollector.negative_targets(user_id, "recommendation")
        pred_bad = FeedbackCollector.negative_targets(user_id, "prediction")
        interview_bad = FeedbackCollector.negative_targets(user_id, "interview")

        insights: list[ImprovementInsight] = []
        adjustments: list[str] = []

        if rec_bad:
            insights.append(
                ImprovementInsight(
                    area="recommendations",
                    issue=f"User flagged {len(rec_bad)} recommendation(s) as not useful",
                    action="Deprioritize similar formats/subjects and diversify suggestions",
                    priority="high",
                )
            )
            adjustments.append(f"Downranked {len(rec_bad)} recommendation target(s)")

        if pred_bad or satisfaction.by_category.get("prediction", {}).get("avg_rating", 5) < 3:
            insights.append(
                ImprovementInsight(
                    area="predictions",
                    issue="Prediction feedback indicates low trust",
                    action="Surface confidence bands and collect actual scores to recalibrate",
                    priority="medium",
                )
            )
            adjustments.append("Prediction UI will emphasize confidence + feedback prompt")

        if interview_bad:
            insights.append(
                ImprovementInsight(
                    area="interview",
                    issue="Interview feedback rated poorly",
                    action="Tune coaching tone and add role-specific question banks",
                    priority="medium",
                )
            )

        if satisfaction.trend == "declining":
            insights.append(
                ImprovementInsight(
                    area="overall",
                    issue="Satisfaction trend is declining",
                    action="Review recent negative comments and adjust agent prompts",
                    priority="high",
                )
            )

        if not insights:
            insights.append(
                ImprovementInsight(
                    area="overall",
                    issue="No major issues detected",
                    action="Keep collecting feedback to refine personalization",
                    priority="low",
                )
            )

        note = _recommendation_note(satisfaction, rec_bad, adjustments)
        return ImprovementLoopResponse(
            user_id=user_id,
            insights=insights,
            downranked_targets=downranked,
            improved_recommendation_note=note,
            applied_adjustments=adjustments,
        )

    @staticmethod
    def filter_recommendations(user_id: str, resources: list) -> list:
        """Remove or deprioritize resources matching negative feedback targets."""
        bad = set(FeedbackCollector.negative_targets(user_id, "recommendation"))
        if not bad:
            return resources

        def _matches(r) -> bool:
            title = getattr(r, "title", "") or ""
            subject = getattr(r, "subject", "") or ""
            fmt = getattr(r, "format", "") or ""
            for b in bad:
                bl = b.lower()
                if bl in title.lower() or bl in subject.lower() or bl in fmt.lower():
                    return True
            return False

        kept = [r for r in resources if not _matches(r)]
        if len(kept) < 3:
            # Keep at least some results — only drop exact title matches
            kept = [r for r in resources if getattr(r, "title", "") not in bad]
        return kept or resources


def _recommendation_note(satisfaction, rec_bad: list[str], adjustments: list[str]) -> str:
    if rec_bad:
        return (
            f"Based on your feedback, we've adjusted future suggestions "
            f"(avoiding: {', '.join(rec_bad[:3])})."
        )
    if satisfaction.total_feedback == 0:
        return "Rate recommendations to help the AI learn your preferences."
    if satisfaction.satisfaction_score >= 80:
        return "Your feedback is positive — we'll keep this personalization style."
    return "We're using your ratings to improve the next batch of recommendations."
