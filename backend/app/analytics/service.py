"""Week 3 Day 5 — Analytics dashboard: risk meter, trends, confidence."""

from __future__ import annotations

from app.models.analytics import AnalyticsCards, AnalyticsDashboard, RiskMeter
from app.models.common import ChartPoint


def _risk_level(score: float) -> str:
    if score >= 75:
        return "low"
    if score >= 60:
        return "medium"
    return "high"


def compute_risk_meter(
    performance_score: float,
    study_hours_week: float = 28.0,
    attendance_pct: float = 80.0,
    sleep_hours: float = 7.0,
) -> RiskMeter:
    """Derive burnout, exam failure, and engagement risk from behavioral signals."""
    exam_failure_risk = round(float(max(0, min(100, (65 - performance_score) * 1.8))), 1)
    if performance_score >= 75:
        exam_failure_risk = round(max(5, exam_failure_risk * 0.3), 1)

    sleep_deficit = max(0, 7 - sleep_hours)
    hour_load = study_hours_week / 7
    burnout_risk = round(
        float(min(100, sleep_deficit * 18 + max(0, hour_load - 5) * 12 + (100 - performance_score) * 0.2)),
        1,
    )

    engagement_index = (attendance_pct * 0.45 + min(hour_load / 6 * 100, 100) * 0.35 + performance_score * 0.2)
    low_engagement_score = round(float(max(0, min(100, 100 - engagement_index))), 1)

    return RiskMeter(
        burnout_risk=burnout_risk,
        exam_failure_risk=exam_failure_risk,
        low_engagement_score=low_engagement_score,
    )


def build_confidence_trends(performance_trend: list[ChartPoint]) -> list[ChartPoint]:
    """Model confidence rising as performance stabilizes week over week."""
    if not performance_trend:
        return [ChartPoint(label="W1", value=62)]
    out: list[ChartPoint] = []
    prev = performance_trend[0].value
    for pt in performance_trend:
        delta = pt.value - prev
        base = 55 + pt.value * 0.35
        conf = base + min(8, max(-5, delta * 0.5))
        out.append(ChartPoint(label=pt.label, value=round(min(98, max(50, conf)), 1)))
        prev = pt.value
    return out


def build_analytics(
    performance_score: float,
    performance_trend: list[ChartPoint],
    subject_distribution: list[ChartPoint],
    study_hours_week: float = 28.5,
    study_streak_days: int = 12,
    attendance_pct: float = 78.0,
    sleep_hours: float = 6.8,
) -> AnalyticsDashboard:
    trend_delta = 0.0
    if len(performance_trend) >= 2:
        trend_delta = round(performance_trend[-1].value - performance_trend[-2].value, 1)

    return AnalyticsDashboard(
        cards=AnalyticsCards(
            ai_score=round(performance_score, 1),
            risk_level=_risk_level(performance_score),
            performance_trend_delta=trend_delta,
            study_streak_days=study_streak_days,
        ),
        risk_meter=compute_risk_meter(
            performance_score,
            study_hours_week=study_hours_week,
            attendance_pct=attendance_pct,
            sleep_hours=sleep_hours,
        ),
        weekly_progress=performance_trend,
        subject_comparison=subject_distribution,
        confidence_trends=build_confidence_trends(performance_trend),
    )
