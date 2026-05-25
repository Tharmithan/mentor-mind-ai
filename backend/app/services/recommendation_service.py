from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Recommendation
from app.models.recommendation import RecommendationItem, RecommendationsResponse

_MOCK_RECOMMENDATIONS = [
    RecommendationItem(
        id="mock-1",
        title="Review Data Structures — Trees & Graphs",
        description="Weak topic detected from last quiz (62%)",
        topic="Data Structures",
        priority="high",
        is_completed=False,
    ),
    RecommendationItem(
        id="mock-2",
        title="Schedule mock technical interview",
        description="Last interview score: 3.8/5 — room to improve",
        topic="Interview",
        priority="medium",
        is_completed=False,
    ),
    RecommendationItem(
        id="mock-3",
        title="Maintain Mathematics momentum",
        description="Strong performance — 91% last assessment",
        topic="Mathematics",
        priority="low",
        is_completed=True,
    ),
]


class RecommendationService:
    @staticmethod
    async def list_for_user(
        session: AsyncSession | None,
    ) -> RecommendationsResponse:
        if session is None:
            return RecommendationsResponse(recommendations=_MOCK_RECOMMENDATIONS)

        result = await session.execute(
            select(Recommendation).order_by(Recommendation.created_at.desc())
        )
        rows = result.scalars().all()
        if not rows:
            return RecommendationsResponse(recommendations=_MOCK_RECOMMENDATIONS)

        return RecommendationsResponse(
            recommendations=[
                RecommendationItem(
                    id=str(r.id),
                    title=r.title,
                    description=r.description,
                    topic=r.topic,
                    priority=r.priority,
                    is_completed=r.is_completed,
                )
                for r in rows
            ]
        )
