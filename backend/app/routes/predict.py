from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models import PredictRequest, PredictResponse
from app.services import PredictionService

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="ML performance prediction",
    description=(
        "Send study hours, attendance %, and sleep hours → get AI prediction "
        'with label (e.g. "High Performance") and confidence 0–100.'
    ),
)
async def predict_performance(
    payload: PredictRequest,
    db: AsyncSession | None = Depends(get_optional_db),
):
    """
    **Day 7 ML API** — uses trained Random Forest when `ml-models/*.joblib` exist.

    **Input example:**
    ```json
    {
      "study_hours": 5,
      "attendance": 82,
      "sleep_hours": 7
    }
    ```

    **Output example:**
    ```json
    {
      "prediction": "High Performance",
      "confidence": 92,
      "predicted_score": 78.5,
      "risk_level": "low",
      "recommendation": "On track — maintain current study pace.",
      "model_version": "random_forest-v1.0"
    }
    ```
    """
    return await PredictionService.predict_performance(payload, db)
