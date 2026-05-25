"""Week 3 Day 7 — Recommendation engine + study planner."""

from app.recommendation.engine import RecommendationEngine, get_recommendation_engine
from app.recommendation.planner import StudyPlannerService

__all__ = [
    "RecommendationEngine",
    "get_recommendation_engine",
    "StudyPlannerService",
]


def __getattr__(name: str):
    if name == "RecommendationService":
        from app.recommendation.service import RecommendationService
        return RecommendationService
    raise AttributeError(name)
