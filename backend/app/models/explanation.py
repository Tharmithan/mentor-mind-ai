from pydantic import BaseModel, Field

from app.models.prediction import PredictRequest, PredictResponse


class FeatureContribution(BaseModel):
    feature: str
    label: str
    contribution_pct: float = Field(ge=0, le=100)
    direction: str = Field(description="positive | negative relative to outcome")
    raw_value: float | None = None


class ExplainResponse(BaseModel):
    """Why the model made this prediction — SHAP or feature importance."""

    prediction: PredictResponse
    method: str = Field(description="shap | feature_importance | heuristic")
    algorithm: str
    explanations: list[str]
    contributions: list[FeatureContribution]
    top_feature: str | None = None
    summary: str


class GlobalExplainResponse(BaseModel):
    method: str
    algorithm: str
    mean_abs_shap: list[FeatureContribution]
    plot_paths: list[str] = []
