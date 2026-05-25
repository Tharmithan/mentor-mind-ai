from app.models.prediction import PredictRequest, PredictResponse


class PredictionService:
    """
    Performance prediction — mock heuristic until ML models (Phase 4).
    Replace with joblib/XGBoost inference from ml-models/.
    """

    @staticmethod
    async def predict_performance(payload: PredictRequest) -> PredictResponse:
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

        return PredictResponse(
            predicted_score=predicted,
            risk_level=risk,
            confidence=confidence,
            recommendation=recommendation,
        )
