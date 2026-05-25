from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession | None = Depends(get_optional_db),
):
    """MVP dashboard stats, chart series, and AI suggestions."""
    return await DashboardService.get_dashboard(db)
