from fastapi import APIRouter

from app.core.cache import cache_stats
from app.database import check_database_connection
from app.middleware.latency import latency_summary
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


@router.get("/metrics/latency")
async def metrics_latency():
    """Per-route latency averages (Week 8 · Day 4)."""
    return {
        "routes": latency_summary(),
        "response_cache": cache_stats(),
    }
