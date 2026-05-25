from app.models.user import UserProfile


class UserService:
    """User operations — mock data until auth (Phase 2) is wired."""

    @staticmethod
    async def get_demo_user() -> UserProfile:
        return UserProfile(
            id="demo-user-001",
            email="student@mentormind.ai",
            full_name="Demo Student",
            role="student",
            xp=1240,
            streak_days=7,
            performance_score=82.0,
        )
