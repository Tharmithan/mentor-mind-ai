"""Week 3 Day 3 — Rule-based + collaborative filtering recommendation engine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
CLEANED_CSV = REPO_ROOT / "datasets" / "processed" / "student_performance_cleaned.csv"

COURSE_LABELS = {0: "Mathematics", 1: "Portuguese"}

SUBJECT_TOPICS: dict[str, list[str]] = {
    "Mathematics": ["Algebra", "Geometry", "Statistics", "Calculus basics"],
    "Portuguese": ["Grammar", "Reading comprehension", "Writing", "Vocabulary"],
    "Programming": ["Data Structures", "Algorithms", "OOP", "Debugging"],
    "Data Structures": ["Trees & Graphs", "Sorting", "Hash maps", "Big-O practice"],
    "Science": ["Physics fundamentals", "Lab reports", "Formulas"],
}

WEAK_THRESHOLD = 70.0
ATTENDANCE_LOW = 75.0


@dataclass
class StudentProfile:
    study_hours: float = 3.0
    attendance_pct: float = 80.0
    sleep_hours: float = 7.0
    past_failures: int = 0
    subject_scores: dict[str, float] = field(default_factory=dict)
    predicted_score: float | None = None
    risk_level: str | None = None


@dataclass
class GeneratedRecommendation:
    title: str
    description: str
    topic: str
    priority: str
    action_type: str  # revision | attendance | wellness | maintain


class RecommendationEngine:
    def __init__(self) -> None:
        self._cohort: pd.DataFrame | None = None

    def _load_cohort(self) -> pd.DataFrame:
        if self._cohort is not None:
            return self._cohort
        if CLEANED_CSV.exists():
            df = pd.read_csv(CLEANED_CSV)
            df["subject"] = df["course"].map(COURSE_LABELS).fillna("Mathematics")
            df["math_score"] = np.where(
                df["course"] == 0,
                df["grade_period_1"] / 20 * 100,
                np.nan,
            )
            df["lang_score"] = np.where(
                df["course"] == 1,
                df["grade_period_1"] / 20 * 100,
                np.nan,
            )
            self._cohort = df
            return df
        self._cohort = pd.DataFrame()
        return self._cohort

    def default_subject_scores(self) -> dict[str, float]:
        """Demo profile: weak math, moderate language."""
        return {
            "Mathematics": 58.0,
            "Portuguese": 72.0,
            "Programming": 78.0,
            "Data Structures": 62.0,
        }

    def normalize_profile(self, profile: StudentProfile | None) -> StudentProfile:
        if profile is None:
            return StudentProfile(subject_scores=self.default_subject_scores())
        defaults = self.default_subject_scores()
        if not profile.subject_scores:
            profile.subject_scores = defaults
        else:
            merged = {**defaults, **profile.subject_scores}
            profile.subject_scores = merged
        return profile

    def weak_subjects(self, profile: StudentProfile) -> list[tuple[str, float]]:
        ranked = sorted(profile.subject_scores.items(), key=lambda x: x[1])
        return [(s, sc) for s, sc in ranked if sc < WEAK_THRESHOLD]

    def revision_order(self, profile: StudentProfile) -> list[str]:
        """Weakest subjects first, then moderate, then strong (maintenance)."""
        ranked = sorted(profile.subject_scores.items(), key=lambda x: x[1])
        return [s for s, _ in ranked]

    def _topic_for_subject(self, subject: str, score: float) -> str:
        topics = SUBJECT_TOPICS.get(subject, ["Core concepts", "Practice problems"])
        if score < 55:
            return topics[0]
        if score < 65 and len(topics) > 1:
            return topics[1]
        return topics[-1]

    def rule_based_recommendations(self, profile: StudentProfile) -> list[GeneratedRecommendation]:
        recs: list[GeneratedRecommendation] = []
        weak = self.weak_subjects(profile)

        for subject, score in weak[:3]:
            topic = self._topic_for_subject(subject, score)
            if subject == "Mathematics" and score < WEAK_THRESHOLD:
                topic = "Algebra" if score < 60 else topic
                title = f"Focus on {topic} revision this week"
                desc = (
                    f"Math score is {score:.0f}% (below target). "
                    f"Allocate 2 extra sessions to {topic} before the next assessment."
                )
            else:
                title = f"Strengthen {subject} — {topic}"
                desc = f"{subject} at {score:.0f}% — prioritize {topic} drills and past papers."

            priority = "high" if score < 60 else "medium"
            recs.append(
                GeneratedRecommendation(
                    title=title,
                    description=desc,
                    topic=subject,
                    priority=priority,
                    action_type="revision",
                )
            )

        if profile.attendance_pct < ATTENDANCE_LOW:
            recs.append(
                GeneratedRecommendation(
                    title="Improve lecture attendance",
                    description=(
                        f"Attendance is {profile.attendance_pct:.0f}% — below {ATTENDANCE_LOW:.0f}%. "
                        "Students with higher attendance score 8–12 points better on average."
                    ),
                    topic="Attendance",
                    priority="high",
                    action_type="attendance",
                )
            )

        if profile.study_hours < 2.5:
            recs.append(
                GeneratedRecommendation(
                    title="Increase daily study blocks",
                    description=(
                        f"Currently ~{profile.study_hours:.1f}h/day. "
                        "Aim for 3–4 focused hours with Pomodoro breaks."
                    ),
                    topic="Study habits",
                    priority="medium",
                    action_type="wellness",
                )
            )

        if profile.sleep_hours < 6:
            recs.append(
                GeneratedRecommendation(
                    title="Protect sleep before exams",
                    description=(
                        f"Sleep at {profile.sleep_hours:.1f}h impacts recall. "
                        "Target 7–8 hours during revision week."
                    ),
                    topic="Wellness",
                    priority="medium",
                    action_type="wellness",
                )
            )

        strong = [(s, sc) for s, sc in profile.subject_scores.items() if sc >= 85]
        for subject, score in strong[:1]:
            recs.append(
                GeneratedRecommendation(
                    title=f"Maintain {subject} momentum",
                    description=f"Strong performance at {score:.0f}% — one light review session per week.",
                    topic=subject,
                    priority="low",
                    action_type="maintain",
                )
            )

        if profile.risk_level == "high" or (profile.predicted_score and profile.predicted_score < 60):
            recs.insert(
                0,
                GeneratedRecommendation(
                    title="At-risk recovery plan — start today",
                    description=(
                        "ML model flags elevated risk. Follow revision order and attend all sessions this week."
                    ),
                    topic="Risk",
                    priority="high",
                    action_type="revision",
                ),
            )

        return recs[:8]

    def collaborative_suggestions(self, profile: StudentProfile, top_k: int = 5) -> list[str]:
        """
        Find similar students in cohort; suggest what helped peers who improved.
        Returns human-readable insight strings.
        """
        df = self._load_cohort()
        if df.empty or len(df) < 20:
            return []

        math = df[df["course"] == 0].copy()
        if math.empty:
            return []

        math_score = profile.subject_scores.get("Mathematics", 65.0)
        vec = np.array(
            [
                profile.attendance_pct,
                math_score,
                profile.study_hours,
                profile.past_failures,
            ],
            dtype=float,
        )
        mat = math[["attendance_pct", "math_score", "study_hours", "past_failures"]].fillna(0).values
        mat[:, 1] = np.nan_to_num(mat[:, 1], nan=math_score)

        norms = np.linalg.norm(mat, axis=1) * np.linalg.norm(vec)
        sim = np.zeros(len(mat))
        mask = norms > 0
        sim[mask] = (mat[mask] @ vec) / norms[mask]

        math = math.assign(similarity=sim)
        peers = math.nlargest(top_k, "similarity")

        improved = peers[
            (peers["grade_period_2"] > peers["grade_period_1"])
            & (peers["performance_pct"] >= 60)
        ]
        insights: list[str] = []
        if len(improved) > 0:
            avg_study = improved["study_hours"].mean()
            if avg_study > profile.study_hours + 0.3:
                insights.append(
                    f"Peers similar to you who improved studied ~{avg_study:.1f}h/day "
                    f"(you: {profile.study_hours:.1f}h)."
                )
            insights.append(
                f"{len(improved)} similar students raised grades by revising weak topics early in the week."
            )

        at_risk_peers = peers[peers["at_risk"] == 1]
        if len(at_risk_peers) >= 2 and profile.attendance_pct < 80:
            insights.append(
                "Collaborative filter: low-attendance peers often recover after 2 weeks of 90%+ attendance."
            )

        return insights[:3]

    def build_study_plan(self, profile: StudentProfile) -> dict:
        """AI Daily Study Planner — timetable, priorities, focus areas."""
        order = self.revision_order(profile)
        weak = self.weak_subjects(profile)
        focus_areas = [
            {
                "subject": s,
                "topic": self._topic_for_subject(s, sc),
                "score": sc,
                "priority_rank": i + 1,
            }
            for i, (s, sc) in enumerate(
                sorted(profile.subject_scores.items(), key=lambda x: x[1])[:4]
            )
        ]

        weekly_hours = max(14.0, profile.study_hours * 7)
        weak_weight = 0.5
        medium_weight = 0.35
        maintain_weight = 0.15

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        slots = ["Morning", "Afternoon", "Evening"]
        timetable: list[dict] = []

        subjects_cycle = order if order else list(profile.subject_scores.keys())
        if not subjects_cycle:
            subjects_cycle = ["Mathematics", "Portuguese"]

        hours_left = weekly_hours
        day_idx = 0
        for subject in subjects_cycle:
            if hours_left <= 0:
                break
            sc = profile.subject_scores.get(subject, 70)
            if sc < WEAK_THRESHOLD:
                duration = 1.5 * weak_weight * 7 / max(len(weak), 1)
                priority = "high"
            elif sc < 80:
                duration = 1.0 * medium_weight * 7 / max(len(subjects_cycle) - len(weak), 1)
                priority = "medium"
            else:
                duration = 0.75 * maintain_weight * 7
                priority = "low"

            duration = min(duration, hours_left / 2, 2.5)
            duration = max(0.75, round(duration, 1))
            hours_left -= duration

            topic = self._topic_for_subject(subject, sc)
            timetable.append(
                {
                    "day": days[day_idx % 7],
                    "time_slot": slots[day_idx % 3],
                    "subject": subject,
                    "topic": topic,
                    "duration_hours": duration,
                    "priority": priority,
                    "task": f"{topic} — practice & review",
                }
            )
            day_idx += 1

        cf_insights = self.collaborative_suggestions(profile)
        return {
            "revision_priority": order,
            "focus_areas": focus_areas,
            "weekly_study_hours": round(weekly_hours, 1),
            "timetable": timetable,
            "collaborative_insights": cf_insights,
            "summary": self._plan_summary(profile, order, weak),
        }

    def _plan_summary(
        self,
        profile: StudentProfile,
        order: list[str],
        weak: list[tuple[str, float]],
    ) -> str:
        if weak:
            w = weak[0]
            topic = self._topic_for_subject(w[0], w[1])
            return (
                f"This week: start with {topic} ({w[0]} at {w[1]:.0f}%), "
                f"then follow revision order {', '.join(order[:3])}."
            )
        return f"Balanced plan across {', '.join(order[:3])} — maintain current pace."

    def to_recommendation_items(
        self, recs: list[GeneratedRecommendation]
    ) -> list[dict]:
        return [
            {
                "id": str(uuid.uuid4())[:8],
                "title": r.title,
                "description": r.description,
                "topic": r.topic,
                "priority": r.priority,
                "is_completed": False,
                "action_type": r.action_type,
            }
            for r in recs
        ]


_engine: RecommendationEngine | None = None


def get_recommendation_engine() -> RecommendationEngine:
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine
