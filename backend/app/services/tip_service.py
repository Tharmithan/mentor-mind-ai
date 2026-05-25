from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User
from app.models.tip import DailyTipResponse

_TIPS = [
    (
        "study",
        "Break study into 25-minute focus blocks — consistency beats long cram sessions.",
    ),
    (
        "interview",
        "Practice explaining your projects out loud; clarity matters as much as code.",
    ),
    (
        "performance",
        "Review one weak topic before learning something new — it compounds your score.",
    ),
    (
        "wellness",
        "Take a 5-minute walk between sessions to reset focus and reduce stress.",
    ),
    (
        "career",
        "Track skills you use weekly — your portfolio should mirror real strengths.",
    ),
]


class TipService:
    @staticmethod
    async def get_daily_tip(session: AsyncSession | None) -> DailyTipResponse:
        weak_topic: str | None = None
        performance_score = 82.0

        if session is not None:
            result = await session.execute(
                select(User)
                .options(selectinload(User.performance_data))
                .limit(1)
            )
            user = result.scalar_one_or_none()
            if user and user.performance_data:
                perf = sorted(user.performance_data, key=lambda p: float(p.score))
                performance_score = sum(float(p.score) for p in perf) / len(perf)
                if perf:
                    weak_topic = perf[0].subject

        day_seed = date.today().toordinal()
        category, base_tip = _TIPS[day_seed % len(_TIPS)]

        if weak_topic and category in ("performance", "study"):
            tip = (
                f"Today's focus: strengthen **{weak_topic}**. "
                f"Spend 30 minutes on fundamentals — your average is {performance_score:.0f}%."
            )
            return DailyTipResponse(
                tip=tip.replace("**", ""),
                category="personalized",
                focus_topic=weak_topic,
            )

        if performance_score < 70:
            tip = (
                f"Your performance is trending at {performance_score:.0f}%. "
                "Prioritize revision on your lowest-scoring subject today."
            )
            return DailyTipResponse(tip=tip, category="personalized", focus_topic=weak_topic)

        return DailyTipResponse(tip=base_tip, category=category, focus_topic=weak_topic)
