"""
Seed demo data for local development.

Usage (from backend/):
  python -m scripts.seed_db
"""
import asyncio
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.auth.passwords import hash_password

from app.database.init_db import create_tables
from app.database.models import (
    InterviewResult,
    PerformanceData,
    Recommendation,
    User,
)
from app.database.session import AsyncSessionLocal


async def seed() -> None:
    await create_tables()

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(User).limit(1))
        if existing:
            print("Database already seeded — skipping.")
            return

        user = User(
            email="student@mentormind.ai",
            password_hash=hash_password("Demo123!"),
            full_name="Demo Student",
            role="student",
            xp=1240,
            streak_days=7,
        )
        session.add(user)
        await session.flush()

        session.add_all(
            [
                PerformanceData(
                    user_id=user.id,
                    subject="Mathematics",
                    score=Decimal("91"),
                    study_hours=Decimal("5"),
                    attendance_pct=Decimal("92"),
                    predicted_score=Decimal("91"),
                    risk_level="low",
                ),
                PerformanceData(
                    user_id=user.id,
                    subject="Programming",
                    score=Decimal("78"),
                    study_hours=Decimal("4"),
                    attendance_pct=Decimal("85"),
                    predicted_score=Decimal("78"),
                    risk_level="medium",
                ),
                PerformanceData(
                    user_id=user.id,
                    subject="Data Structures",
                    score=Decimal("62"),
                    study_hours=Decimal("3"),
                    attendance_pct=Decimal("70"),
                    predicted_score=Decimal("62"),
                    risk_level="high",
                ),
                InterviewResult(
                    user_id=user.id,
                    mode="technical",
                    overall_score=Decimal("4.2"),
                    communication_score=Decimal("4.2"),
                    technical_score=Decimal("3.8"),
                    confidence_score=Decimal("72"),
                    feedback_summary="Strong communication; improve technical depth.",
                ),
                Recommendation(
                    user_id=user.id,
                    title="Review Data Structures — Trees & Graphs",
                    description="Weak topic detected from last quiz (62%)",
                    topic="Data Structures",
                    priority="high",
                ),
                Recommendation(
                    user_id=user.id,
                    title="Schedule mock technical interview",
                    description="Last interview score: 3.8/5 — room to improve",
                    topic="Interview",
                    priority="medium",
                ),
                Recommendation(
                    user_id=user.id,
                    title="Maintain Mathematics momentum",
                    description="Strong performance — 91% last assessment",
                    topic="Mathematics",
                    priority="low",
                    is_completed=True,
                ),
            ]
        )

        await session.commit()
        print(f"Seeded demo user: {user.email} (id={user.id})")
        print("Demo login: student@mentormind.ai / Demo123!")


if __name__ == "__main__":
    asyncio.run(seed())
