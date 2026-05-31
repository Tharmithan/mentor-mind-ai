"""Shared pytest fixtures (Week 8 · Day 3)."""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Env before app import so settings + engine use test config
os.environ.setdefault("JWT_SECRET", "pytest-secret-key-not-for-production")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("AUTH_RATE_LIMIT_PER_MINUTE", "10000")
os.environ.setdefault("DEBUG", "true")

from app.database import get_optional_db  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.database.models import (  # noqa: F401,E402
    InterviewResult,
    PerformanceData,
    Recommendation,
    RefreshToken,
    User,
)
from app.main import app  # noqa: E402


def _make_engine():
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


async def _init_db(engine) -> async_sessionmaker[AsyncSession]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
def db_engine():
    engine = _make_engine()
    session_factory = asyncio.run(_init_db(engine))
    yield engine, session_factory
    asyncio.run(engine.dispose())


@pytest.fixture
def client(db_engine):
    engine, session_factory = db_engine

    async def override_get_optional_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_optional_db] = override_get_optional_db
    if hasattr(app.state, "limiter"):
        app.state.limiter.enabled = False

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def auth_headers(client, unique_email) -> dict[str, str]:
    """Register a user and return Authorization headers."""
    password = "TestPass1"
    reg = client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": password, "full_name": "Test User"},
    )
    assert reg.status_code == 200, reg.text
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
