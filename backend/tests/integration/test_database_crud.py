"""Integration tests — database CRUD & consistency (Week 8 · Day 3)."""

from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.auth.passwords import hash_password
from app.database.models import PerformanceData, Recommendation, User


@pytest.mark.asyncio
async def test_user_crud_and_relationships(db_engine):
    _, session_factory = db_engine

    async with session_factory() as session:
        user = User(
            email=f"db-{uuid.uuid4().hex[:6]}@test.com",
            password_hash=hash_password("SecurePass1"),
            full_name="DB Test",
            role="student",
        )
        session.add(user)
        await session.flush()

        session.add(
            PerformanceData(
                user_id=user.id,
                subject="Math",
                score=Decimal("88.5"),
                study_hours=Decimal("4"),
                attendance_pct=Decimal("90"),
                predicted_score=Decimal("87"),
                risk_level="low",
            )
        )
        session.add(
            Recommendation(
                user_id=user.id,
                title="Review algebra",
                description="Weak area detected",
                topic="Math",
                priority="high",
            )
        )
        await session.commit()

        uid = user.id

    async with session_factory() as session:
        loaded = await session.scalar(select(User).where(User.id == uid))
        assert loaded is not None
        assert loaded.full_name == "DB Test"

        perf = (
            await session.scalars(
                select(PerformanceData).where(PerformanceData.user_id == uid)
            )
        ).all()
        assert len(perf) == 1
        assert float(perf[0].score) == pytest.approx(88.5)

        recs = (
            await session.scalars(
                select(Recommendation).where(Recommendation.user_id == uid)
            )
        ).all()
        assert len(recs) == 1
        assert recs[0].title == "Review algebra"


def test_register_persists_user(client, unique_email):
    """API signup writes a row the DB can read back via login."""
    reg = client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": "SecurePass1", "full_name": "Persisted"},
    )
    assert reg.status_code == 200

    login = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "SecurePass1"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == unique_email
