from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models.recommendation import RecommendationsResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/recommendations", response_model=RecommendationsResponse)
async def list_recommendations(
    db: AsyncSession | None = Depends(get_optional_db),
):
    """List AI recommendations (database or mock fallback)."""
    return await RecommendationService.list_for_user(db)
