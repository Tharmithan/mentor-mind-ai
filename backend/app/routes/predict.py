from fastapi import APIRouter

from app.models import PredictRequest, PredictResponse
from app.services import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict_performance(payload: PredictRequest):
    """Predict student performance from study metrics."""
    return await PredictionService.predict_performance(payload)
