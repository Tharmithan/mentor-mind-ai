from app.database.base import Base
from app.database.models import (  # noqa: F401 — register models with metadata
    InterviewResult,
    PerformanceData,
    Recommendation,
    User,
)
from app.database.session import engine


async def create_tables() -> None:
    """Create all ORM tables (dev/local). Prefer Supabase SQL for production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all tables — dev only."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
