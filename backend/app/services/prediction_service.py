from decimal import Decimal
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PerformanceData
from app.ai.predictor import get_predictor
from app.models.prediction import PredictRequest, PredictResponse


class PredictionService:
    @staticmethod
    async def predict_performance(
        payload: PredictRequest,
        session: AsyncSession | None = None,
    ) -> PredictResponse:
        result = await asyncio.to_thread(get_predictor().predict, payload)

        try:
            from app.monitoring.service import MonitoringService

            log_id = MonitoringService.log_prediction(
                user_id="demo-user-001",
                predicted_score=result.predicted_score,
                prediction_label=result.prediction,
                model_version=result.model_version,
                inputs={
                    "study_hours": payload.study_hours,
                    "attendance": payload.attendance_value,
                    "sleep_hours": payload.sleep_hours,
                },
            )
            result = result.model_copy(update={"monitoring_log_id": log_id})
        except Exception:
            pass

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
                        attendance_pct=Decimal(str(payload.attendance_value)),
                        predicted_score=Decimal(str(result.predicted_score)),
                        risk_level=result.risk_level,
                    )
                )
                await session.commit()

        return result
