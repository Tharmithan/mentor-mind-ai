from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import PredictRequest, PredictResponse
from app.services import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict_performance(
    payload: PredictRequest,
    db: AsyncSession = Depends(get_db),
):
    """Predict student performance; saves row to performance_data when DB is available."""
    return await PredictionService.predict_performance(payload, db)
