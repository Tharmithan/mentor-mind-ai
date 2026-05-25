from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PerformanceData
from app.models.prediction import PredictRequest, PredictResponse


class PredictionService:
    @staticmethod
    async def predict_performance(
        payload: PredictRequest,
        session: AsyncSession | None = None,
    ) -> PredictResponse:
        weighted = (
            payload.prior_score * 0.5
            + payload.attendance_pct * 0.3
            + min(payload.study_hours / 6 * 100, 100) * 0.2
        )
        quiz_bonus = min(payload.quizzes_completed * 2, 10)
        predicted = round(min(100, weighted + quiz_bonus), 1)

        if predicted >= 75:
            risk = "low"
            recommendation = "On track — maintain current study pace."
        elif predicted >= 60:
            risk = "medium"
            recommendation = "Review weak topics and increase practice quizzes."
        else:
            risk = "high"
            recommendation = "At-risk — schedule extra study sessions and a mock interview."

        confidence = round(0.72 + (predicted / 100) * 0.2, 2)

        if session is not None:
            from sqlalchemy import select

            from app.database.models import User

            user = await session.scalar(select(User).limit(1))
            if user:
                session.add(
                    PerformanceData(
                        user_id=user.id,
                        subject="General",
                        score=Decimal(str(payload.prior_score)),
                        study_hours=Decimal(str(payload.study_hours)),
                        attendance_pct=Decimal(str(payload.attendance_pct)),
                        predicted_score=Decimal(str(predicted)),
                        risk_level=risk,
                    )
                )
                await session.commit()

        return PredictResponse(
            predicted_score=predicted,
            risk_level=risk,
            confidence=confidence,
            recommendation=recommendation,
        )
