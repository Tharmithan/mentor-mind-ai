from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User
from app.models.user import UserProfile


class UserService:
    @staticmethod
    async def get_demo_user(session: AsyncSession | None = None) -> UserProfile:
        if session is None:
            return UserService._mock_profile()

        result = await session.execute(
            select(User)
            .options(
                selectinload(User.performance_data),
                selectinload(User.interview_results),
            )
            .limit(1)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return UserService._mock_profile()

        avg_score = 82.0
        if user.performance_data:
            avg_score = sum(float(p.score) for p in user.performance_data) / len(
                user.performance_data
            )

        return UserProfile(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name or "Student",
            role=user.role,
            xp=user.xp,
            streak_days=user.streak_days,
            performance_score=round(avg_score, 1),
        )

    @staticmethod
    def _mock_profile() -> UserProfile:
        return UserProfile(
            id="demo-user-001",
            email="student@mentormind.ai",
            full_name="Demo Student",
            role="student",
            xp=1240,
            streak_days=7,
            performance_score=82.0,
        )
