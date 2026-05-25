from app.models.common import HealthResponse
from app.models.prediction import PredictRequest, PredictResponse, StudentRiskDetection
from app.models.recommendation import RecommendationItem, RecommendationsResponse
from app.models.user import UserProfile, UserResponse

__all__ = [
    "HealthResponse",
    "UserProfile",
    "UserResponse",
    "PredictRequest",
    "PredictResponse",
    "StudentRiskDetection",
    "RecommendationItem",
    "RecommendationsResponse",
]
