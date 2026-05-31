from fastapi import APIRouter

from app.database import check_database_connection
from app.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    db_ok = await check_database_connection()
    return HealthResponse(
        status="healthy",
        service="mentormind-api",
        version="0.9.0",
        database="connected" if db_ok else "not_connected",
    )
