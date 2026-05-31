"""Learning pattern detection from behavior signals (Week 7 · Day 3)."""

from __future__ import annotations

from app.models.common import ChartPoint
from app.models.learning_analytics import LearningPatterns

DAY_TO_TIME: dict[str, str] = {
    "Mon": "morning",
    "Tue": "morning",
    "Wed": "afternoon",
    "Thu": "afternoon",
    "Fri": "evening",
    "Sat": "evening",
    "Sun": "evening",
}


class PatternDetector:
    @staticmethod
    def detect(
        subject_scores: dict[str, float],
        weak_subjects: list[str],
        strong_subjects: list[str],
        preferred_study_time: str,
        study_hours_by_day: list[ChartPoint],
        study_hours_week: float,
        study_streak: int,
        burnout_risk: float,
    ) -> LearningPatterns:
        best_days = PatternDetector._best_days(study_hours_by_day)
        inferred_time = PatternDetector._infer_best_time(study_hours_by_day, preferred_study_time)
        productivity = PatternDetector._productivity_narrative(
            study_hours_week, study_streak, weak_subjects, best_days
        )
        burnout_level = (
            "high" if burnout_risk >= 65 else "medium" if burnout_risk >= 40 else "low"
        )

        return LearningPatterns(
            best_study_time=inferred_time,
            best_study_days=best_days,
            productivity_pattern=productivity,
            weak_learning_areas=weak_subjects[:5],
            strong_learning_areas=strong_subjects[:5],
            burnout_risk=round(burnout_risk, 1),
            burnout_level=burnout_level,
        )

    @staticmethod
    def _best_days(hours: list[ChartPoint]) -> list[str]:
        if not hours:
            return ["Thu", "Sat"]
        ranked = sorted(hours, key=lambda h: -h.value)
        return [h.label for h in ranked[:2]]

    @staticmethod
    def _infer_best_time(hours: list[ChartPoint], preferred: str) -> str:
        if not hours:
            return preferred or "evening"
        peak = max(hours, key=lambda h: h.value)
        mapped = DAY_TO_TIME.get(peak.label, preferred)
        # Blend explicit preference with observed peak
        if preferred and preferred != mapped:
            return preferred
        return mapped

    @staticmethod
    def _productivity_narrative(
        hours_week: float,
        streak: int,
        weak: list[str],
        best_days: list[str],
    ) -> str:
        daily = hours_week / 7 if hours_week else 0
        if daily >= 4 and streak >= 7:
            return (
                f"High productivity — {hours_week:.0f}h/week with a {streak}-day streak. "
                f"Peak output on {', '.join(best_days)}."
            )
        if daily >= 2.5:
            return (
                f"Steady rhythm — ~{daily:.1f}h/day. Focus {', '.join(weak[:2]) or 'weak areas'} "
                f"on {best_days[0] if best_days else 'Thu'} for best retention."
            )
        return (
            f"Room to grow — aim for 3h/day. Schedule deep work on "
            f"{', '.join(best_days) or 'weekends'} when energy is highest."
        )
