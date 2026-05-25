from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Recommendation
from app.models.recommendation import RecommendationItem, RecommendationsResponse


class RecommendationService:
    @staticmethod
    async def list_for_user(session: AsyncSession) -> RecommendationsResponse:
        result = await session.execute(
            select(Recommendation).order_by(Recommendation.created_at.desc())
        )
        rows = result.scalars().all()
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
