"""AI Learning Analytics routes (Week 7 · Day 3).

    GET /api/learning-analytics/{user_id}   full analytics dashboard
    GET /api/learning-analytics/demo        demo user analytics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.learning_engine import LearningAnalyticsEngine
from app.database import get_optional_db
from app.models.learning_analytics import LearningAnalyticsDashboard
from app.services.user_service import UserService

router = APIRouter(prefix="/learning-analytics", tags=["learning-analytics"])


@router.get("/demo", response_model=LearningAnalyticsDashboard)
async def demo_analytics(
    db: AsyncSession | None = Depends(get_optional_db),
) -> LearningAnalyticsDashboard:
    user = await UserService.get_demo_user(db)
    return await LearningAnalyticsEngine.analyze(user.id, db)


@router.get("/{user_id}", response_model=LearningAnalyticsDashboard)
async def user_analytics(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> LearningAnalyticsDashboard:
    return await LearningAnalyticsEngine.analyze(user_id, db)
