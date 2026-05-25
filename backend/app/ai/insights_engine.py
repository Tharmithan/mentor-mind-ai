"""Week 3 Day 4 — AI Insights: trend analysis + human-like summaries."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
CLEANED_CSV = REPO_ROOT / "datasets" / "processed" / "student_performance_cleaned.csv"
COHORT_INSIGHTS_JSON = REPO_ROOT / "datasets" / "processed" / "eda" / "ai_insights_report.json"
RESULTS_METRICS = REPO_ROOT / "results" / "metrics" / "ai_insights.json"
RESULTS_REPORT = REPO_ROOT / "results" / "reports" / "ai_insights_summary.md"

COURSE_LABELS = {0: "Mathematics", 1: "Portuguese"}
CODING_SUBJECTS = {"Programming", "Data Structures", "Mathematics"}


@dataclass
class StudentSnapshot:
    study_hours: float = 3.0
    attendance_pct: float = 80.0
    sleep_hours: float = 7.0
    subject_scores: dict[str, float] = field(default_factory=dict)
    previous_attendance_pct: float | None = None
    previous_subject_scores: dict[str, float] = field(default_factory=dict)
    performance_score: float | None = None


@dataclass
class InsightRecord:
    category: str
    message: str
    severity: str = "info"
    metric: str | None = None
    trend_direction: str | None = None
    impact_pct: float | None = None


class InsightsEngine:
    def __init__(self) -> None:
        self._df: pd.DataFrame | None = None
        self._cohort_insights: list[dict] = []

    def _load_data(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df
        if CLEANED_CSV.exists():
            df = pd.read_csv(CLEANED_CSV)
            df["subject"] = df["course"].map(COURSE_LABELS).fillna("General")
            self._df = df
            return df
        self._df = pd.DataFrame()
        return self._df

    def _load_cohort_insights(self) -> list[dict]:
        if self._cohort_insights:
            return self._cohort_insights
        if COHORT_INSIGHTS_JSON.exists():
            data = json.loads(COHORT_INSIGHTS_JSON.read_text())
            self._cohort_insights = data.get("insights", [])
        return self._cohort_insights

    def _default_scores(self) -> dict[str, float]:
        return {
            "Mathematics": 58.0,
            "Portuguese": 72.0,
            "Programming": 78.0,
            "Data Structures": 62.0,
        }

    def normalize_snapshot(self, snap: StudentSnapshot | None) -> StudentSnapshot:
        if snap is None:
            return StudentSnapshot(subject_scores=self._default_scores())
        if not snap.subject_scores:
            snap.subject_scores = self._default_scores()
        else:
            snap.subject_scores = {**self._default_scores(), **snap.subject_scores}
        if snap.performance_score is None:
            snap.performance_score = float(np.mean(list(snap.subject_scores.values())))
        return snap

    def cohort_statistics(self) -> dict:
        df = self._load_data()
        if df.empty:
            return {}
        return {
            "students": len(df),
            "avg_performance": round(df["performance_pct"].mean(), 1),
            "avg_attendance": round(df["attendance_pct"].mean(), 1),
            "avg_study_hours": round(df["study_hours"].mean(), 2),
            "at_risk_rate": round(df["at_risk"].mean() * 100, 1),
            "sleep_performance_gap": self._sleep_gap(df),
            "attendance_impact_pct": self._attendance_impact(df),
        }

    def _sleep_gap(self, df: pd.DataFrame) -> float:
        low = df[df["wellness_score"] <= 2]["performance_pct"].mean()
        high = df[df["wellness_score"] >= 4]["performance_pct"].mean()
        if np.isnan(low) or np.isnan(high):
            return 0.0
        return round(high - low, 1)

    def _attendance_impact(self, df: pd.DataFrame) -> float:
        low = df[df["attendance_pct"] < 90]["performance_pct"].mean()
        high = df[df["attendance_pct"] >= 95]["performance_pct"].mean()
        if np.isnan(low) or np.isnan(high):
            return 0.0
        return round(high - low, 1)

    def trend_analysis(self, snap: StudentSnapshot) -> list[InsightRecord]:
        """Month-over-month style trends from student snapshot."""
        insights: list[InsightRecord] = []

        if snap.previous_attendance_pct is not None:
            delta = snap.attendance_pct - snap.previous_attendance_pct
            if delta <= -5:
                insights.append(
                    InsightRecord(
                        category="attendance_trend",
                        message=(
                            f"Your attendance dropped {abs(delta):.0f}% this month "
                            f"({snap.previous_attendance_pct:.0f}% → {snap.attendance_pct:.0f}%)."
                        ),
                        severity="warning",
                        metric="attendance_pct",
                        trend_direction="down",
                        impact_pct=round(abs(delta), 1),
                    )
                )
            elif delta >= 5:
                insights.append(
                    InsightRecord(
                        category="attendance_trend",
                        message=(
                            f"Your attendance improved {delta:.0f}% this month — "
                            "keep showing up to lectures."
                        ),
                        severity="positive",
                        metric="attendance_pct",
                        trend_direction="up",
                        impact_pct=round(delta, 1),
                    )
                )

        if snap.previous_subject_scores:
            coding_deltas = []
            for subj in CODING_SUBJECTS:
                if subj in snap.subject_scores and subj in snap.previous_subject_scores:
                    d = snap.subject_scores[subj] - snap.previous_subject_scores[subj]
                    coding_deltas.append((subj, d))
            if coding_deltas:
                avg_delta = np.mean([d for _, d in coding_deltas])
                if avg_delta >= 3:
                    best = max(coding_deltas, key=lambda x: x[1])
                    insights.append(
                        InsightRecord(
                            category="subject_improvement",
                            message=(
                                "You are improving faster in coding-related subjects — "
                                f"{best[0]} gained {best[1]:.0f} points recently."
                            ),
                            severity="positive",
                            metric="subject_scores",
                            trend_direction="up",
                            impact_pct=round(avg_delta, 1),
                        )
                    )
                elif avg_delta <= -3:
                    insights.append(
                        InsightRecord(
                            category="subject_improvement",
                            message=(
                                "Coding subject scores dipped this month — "
                                "schedule extra practice before the next assessment."
                            ),
                            severity="warning",
                            trend_direction="down",
                            impact_pct=round(abs(avg_delta), 1),
                        )
                    )

        overall_prev = (
            float(np.mean(list(snap.previous_subject_scores.values())))
            if snap.previous_subject_scores
            else None
        )
        if overall_prev is not None and snap.performance_score is not None:
            delta = snap.performance_score - overall_prev
            if abs(delta) >= 2:
                direction = "up" if delta > 0 else "down"
                insights.append(
                    InsightRecord(
                        category="performance_trend",
                        message=(
                            f"Overall performance is trending {direction} "
                            f"({overall_prev:.0f}% → {snap.performance_score:.0f}%)."
                        ),
                        severity="positive" if delta > 0 else "warning",
                        trend_direction=direction,
                        impact_pct=round(abs(delta), 1),
                    )
                )

        return insights

    def cohort_insights_humanized(self) -> list[InsightRecord]:
        records = []
        for item in self._load_cohort_insights()[:4]:
            records.append(
                InsightRecord(
                    category=item.get("category", "cohort"),
                    message=item.get("insight", ""),
                    severity="info",
                    metric=item.get("metric"),
                    impact_pct=item.get("impact_pct"),
                )
            )
        stats = self.cohort_statistics()
        if stats.get("sleep_performance_gap", 0) >= 4:
            records.append(
                InsightRecord(
                    category="wellness_sleep",
                    message=(
                        "Students with consistent sleep patterns perform better — "
                        f"high-wellness peers score ~{stats['sleep_performance_gap']:.0f}% higher on average."
                    ),
                    severity="info",
                    metric="wellness_score",
                    impact_pct=stats["sleep_performance_gap"],
                )
            )
        return records

    def personalized_insights(self, snap: StudentSnapshot) -> list[InsightRecord]:
        insights = self.trend_analysis(snap)
        stats = self.cohort_statistics()

        if snap.attendance_pct < 75 and stats:
            gap = stats.get("attendance_impact_pct", 6)
            insights.append(
                InsightRecord(
                    category="attendance",
                    message=(
                        f"Your attendance is {snap.attendance_pct:.0f}% — "
                        f"cohort data shows {gap:.0f}% higher scores when attendance stays above 90%."
                    ),
                    severity="warning",
                    metric="attendance_pct",
                )
            )

        if snap.sleep_hours < 6.5 and stats.get("sleep_performance_gap"):
            insights.append(
                InsightRecord(
                    category="wellness_sleep",
                    message=(
                        f"At {snap.sleep_hours:.1f}h sleep, you may be below the wellness sweet spot. "
                        "Students with consistent sleep patterns perform better."
                    ),
                    severity="info",
                    metric="sleep_hours",
                )
            )

        weak = sorted(snap.subject_scores.items(), key=lambda x: x[1])
        if weak:
            subj, score = weak[0]
            insights.append(
                InsightRecord(
                    category="weak_subject",
                    message=f"Your lowest subject is {subj} ({score:.0f}%) — prioritize revision this week.",
                    severity="warning" if score < 65 else "info",
                    metric="subject_scores",
                )
            )

        strong_coding = [
            (s, sc)
            for s, sc in snap.subject_scores.items()
            if s in CODING_SUBJECTS and sc >= 75
        ]
        if len(strong_coding) >= 2:
            names = ", ".join(s for s, _ in strong_coding[:2])
            insights.append(
                InsightRecord(
                    category="subject_strength",
                    message=f"You are performing well in coding subjects ({names}).",
                    severity="positive",
                    trend_direction="up",
                )
            )

        return insights

    def generate_all(self, snap: StudentSnapshot | None = None) -> dict:
        snap = self.normalize_snapshot(snap)
        personal = self.personalized_insights(snap)
        cohort = self.cohort_insights_humanized()
        all_insights = personal + cohort

        summary = self.performance_summary(snap, all_insights)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "insights": [self._insight_to_dict(i) for i in all_insights],
            "trends": [self._insight_to_dict(i) for i in personal if i.trend_direction],
            "performance_summary": summary,
            "cohort_stats": self.cohort_statistics(),
        }

    def _insight_to_dict(self, ins: InsightRecord) -> dict:
        return {
            "id": str(uuid.uuid4())[:8],
            "category": ins.category,
            "message": ins.message,
            "severity": ins.severity,
            "metric": ins.metric,
            "trend_direction": ins.trend_direction,
            "impact_pct": ins.impact_pct,
        }

    def performance_summary(
        self, snap: StudentSnapshot, insights: list[InsightRecord] | list[dict]
    ) -> dict:
        score = snap.performance_score or 70.0
        if score >= 75:
            headline = "Strong overall performance"
            trend_label = "on track"
        elif score >= 60:
            headline = "Steady progress with room to grow"
            trend_label = "moderate"
        else:
            headline = "Performance needs attention"
            trend_label = "at-risk"

        if insights and isinstance(insights[0], InsightRecord):
            highlights = [i.message for i in insights[:4]]
        elif insights and isinstance(insights[0], dict):
            highlights = [i.get("message", "") for i in insights[:4]]
        else:
            highlights = []

        weakest = min(snap.subject_scores.items(), key=lambda x: x[1]) if snap.subject_scores else ("—", 0)
        summary_text = (
            f"{headline} ({score:.0f}% average). "
            f"Focus area: {weakest[0]} ({weakest[1]:.0f}%). "
            f"Attendance {snap.attendance_pct:.0f}%, study {snap.study_hours:.1f}h/day."
        )

        return {
            "headline": headline,
            "overall_score": round(score, 1),
            "trend_label": trend_label,
            "highlights": highlights,
            "summary_text": summary_text,
        }

    def natural_language_report(self, payload: dict, llm_text: str | None = None) -> str:
        if llm_text:
            return llm_text
        summary = payload["performance_summary"]
        lines = [
            "# AI Performance Insights Report",
            "",
            f"*Generated: {payload['generated_at']}*",
            "",
            "## Summary",
            "",
            summary["summary_text"],
            "",
            f"**Overall score:** {summary['overall_score']}% · **Status:** {summary['trend_label']}",
            "",
            "## Key insights",
            "",
        ]
        for i, ins in enumerate(payload["insights"][:8], 1):
            lines.append(f"{i}. {ins['message']}")
        if payload.get("cohort_stats"):
            cs = payload["cohort_stats"]
            lines.extend(
                [
                    "",
                    "## Cohort context",
                    "",
                    f"- {cs.get('students', 0)} students analyzed",
                    f"- Average performance: {cs.get('avg_performance', 0)}%",
                    f"- At-risk rate: {cs.get('at_risk_rate', 0)}%",
                ]
            )
        return "\n".join(lines)

    def persist_results(self, payload: dict, nl_report: str) -> None:
        RESULTS_METRICS.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_REPORT.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_METRICS.write_text(json.dumps(payload, indent=2))
        RESULTS_REPORT.write_text(nl_report)


_engine: InsightsEngine | None = None


def get_insights_engine() -> InsightsEngine:
    global _engine
    if _engine is None:
        _engine = InsightsEngine()
    return _engine
