from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.ml.explainer import get_explainer
from app.ml.predictor import get_predictor
from app.models.explanation import ExplainResponse, FeatureContribution, GlobalExplainResponse
from app.models.prediction import PredictRequest
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/predict/explain", response_model=ExplainResponse)
async def explain_prediction(
    payload: PredictRequest,
    db: AsyncSession | None = Depends(get_optional_db),
):
    """
    Predict + explain WHY — SHAP or feature importance.

    Example: "Low attendance contributed 38% to predicted low performance."
    """
    prediction = await PredictionService.predict_performance(payload, db)
    explainer = get_explainer()
    at_risk = prediction.student_risk.high_risk or prediction.predicted_score < 60
    raw = explainer.explain(payload, prediction.predicted_score, at_risk)

    contributions = [FeatureContribution(**c) for c in raw["contributions"]]
    return ExplainResponse(
        prediction=prediction,
        method=raw["method"],
        algorithm=raw["algorithm"],
        explanations=raw["explanations"],
        contributions=contributions,
        top_feature=raw.get("top_feature"),
        summary=raw["explanations"][0] if raw["explanations"] else "",
    )


@router.post("/explain", response_model=ExplainResponse)
async def explain_only(payload: PredictRequest):
    """Explain without saving to DB."""
    prediction = get_predictor().predict(payload)
    at_risk = prediction.student_risk.high_risk or prediction.predicted_score < 60
    raw = get_explainer().explain(payload, prediction.predicted_score, at_risk)
    contributions = [FeatureContribution(**c) for c in raw["contributions"]]
    return ExplainResponse(
        prediction=prediction,
        method=raw["method"],
        algorithm=raw["algorithm"],
        explanations=raw["explanations"],
        contributions=contributions,
        top_feature=raw.get("top_feature"),
        summary=raw["explanations"][0] if raw["explanations"] else "",
    )


@router.get("/explain/global", response_model=GlobalExplainResponse)
async def global_explanation():
    """Precomputed global SHAP from `explain_model.py`."""
    data = get_explainer().global_importance()
    if not data:
        return GlobalExplainResponse(
            method="unavailable",
            algorithm="none",
            mean_abs_shap=[],
            plot_paths=[],
        )
    contribs = [
        FeatureContribution(
            feature=r["feature"],
            label=r["label"],
            contribution_pct=r["contribution_pct"],
            direction=r.get("direction", "risk"),
            raw_value=r.get("mean_abs_shap"),
        )
        for r in data.get("mean_abs_shap", [])
    ]
    return GlobalExplainResponse(
        method=data.get("method", "shap"),
        algorithm=data.get("algorithm", "unknown"),
        mean_abs_shap=contribs,
        plot_paths=[
            "results/graphs/shap_summary.png",
            "results/graphs/shap_feature_importance.png",
        ],
    )
