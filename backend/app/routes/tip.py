from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models.tip import DailyTipResponse
from app.services.tip_service import TipService

router = APIRouter()


@router.get("/daily-tip", response_model=DailyTipResponse)
async def get_daily_tip(
    db: AsyncSession | None = Depends(get_optional_db),
):
    """Daily AI tip — personalized when database data is available."""
    return await TipService.get_daily_tip(db)
