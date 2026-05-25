from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Require a working database connection (raises if unavailable)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_optional_db() -> AsyncGenerator[AsyncSession | None, None]:
    """Yield a DB session when connected; otherwise None (mock fallback in services)."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            try:
                yield session
            finally:
                await session.close()
    except Exception:
        yield None


async def check_database_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
