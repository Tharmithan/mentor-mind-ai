from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models import PredictRequest, PredictResponse
from app.services import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict_performance(
    payload: PredictRequest,
    db: AsyncSession | None = Depends(get_optional_db),
):
    """Predict student performance; saves to DB when connected."""
    return await PredictionService.predict_performance(payload, db)
