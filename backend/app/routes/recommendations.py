from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.recommendation import RecommendationsResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/recommendations", response_model=RecommendationsResponse)
async def list_recommendations(db: AsyncSession = Depends(get_db)):
    """List AI recommendations for the demo user."""
    return await RecommendationService.list_for_user(db)
