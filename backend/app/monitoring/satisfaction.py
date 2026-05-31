"""User satisfaction tracking (Week 7 · Day 6)."""

from __future__ import annotations

from app.models.monitoring import SatisfactionSummary
from app.monitoring.store import get_monitoring_store


class SatisfactionTracker:
    @staticmethod
    def summarize(user_id: str) -> SatisfactionSummary:
        store = get_monitoring_store()
        items = [e for e in store.load_feedback() if e.get("user_id") == user_id]

        if not items:
            return SatisfactionSummary(
                user_id=user_id,
                total_feedback=0,
                avg_rating=0.0,
                helpful_pct=0.0,
                by_category={},
                trend="stable",
                satisfaction_score=70.0,
            )

        ratings = [e.get("rating", 3) for e in items]
        helpful = sum(1 for e in items if e.get("helpful", True))
        avg = sum(ratings) / len(ratings)
        helpful_pct = round(100 * helpful / len(items), 1)

        by_cat: dict[str, dict] = {}
        for e in items:
            cat = e.get("category", "general")
            if cat not in by_cat:
                by_cat[cat] = {"count": 0, "ratings": [], "helpful": 0}
            by_cat[cat]["count"] += 1
            by_cat[cat]["ratings"].append(e.get("rating", 3))
            if e.get("helpful", True):
                by_cat[cat]["helpful"] += 1

        for cat, data in by_cat.items():
            rs = data.pop("ratings")
            data["avg_rating"] = round(sum(rs) / len(rs), 2)
            data["helpful_pct"] = round(100 * data["helpful"] / data["count"], 1)

        trend = _trend(items)
        score = round(min(100, avg * 18 + helpful_pct * 0.28), 1)

        return SatisfactionSummary(
            user_id=user_id,
            total_feedback=len(items),
            avg_rating=round(avg, 2),
            helpful_pct=helpful_pct,
            by_category=by_cat,
            trend=trend,
            satisfaction_score=score,
        )


def _trend(items: list[dict]) -> str:
    if len(items) < 4:
        return "stable"
    mid = len(items) // 2
    first_avg = sum(e.get("rating", 3) for e in items[:mid]) / mid
    second_avg = sum(e.get("rating", 3) for e in items[mid:]) / (len(items) - mid)
    if second_avg - first_avg >= 0.5:
        return "improving"
    if first_avg - second_avg >= 0.5:
        return "declining"
    return "stable"
