"""
Week 3 Day 7 — Unified AI platform routes.

Canonical:
  POST /predict
  POST /recommend
  GET  /analytics
  GET  /insights
"""

import asyncio

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import InsightsService, get_explainer, get_predictor
from app.analytics.service import build_analytics
from app.core.cache import ttl_cache
from app.database import get_optional_db
from app.models.ai_platform import (
    AIPlatformStatus,
    AnalyticsAPIResponse,
    RecommendRequest,
    RecommendResponse,
)
from app.models.common import ChartPoint
from app.models.explanation import ExplainResponse, FeatureContribution
from app.models.insights import InsightsRequest, InsightsResponse
from app.models.prediction import PredictRequest, PredictResponse
from app.models.study_plan import SubjectScoreInput
from app.recommendation import StudyPlannerService
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["AI Platform"])


@router.post("/predict", response_model=PredictResponse)
async def predict(
    payload: PredictRequest,
    db: AsyncSession | None = Depends(get_optional_db),
):
    """ML performance prediction (Random Forest / XGBoost)."""
    return await PredictionService.predict_performance(payload, db)


@router.post("/predict/explain", response_model=ExplainResponse)
async def predict_with_explanation(
    payload: PredictRequest,
    db: AsyncSession | None = Depends(get_optional_db),
):
    """Predict + SHAP explainability."""
    prediction = await PredictionService.predict_performance(payload, db)
    at_risk = prediction.student_risk.high_risk or prediction.predicted_score < 60
    raw = await asyncio.to_thread(
        get_explainer().explain, payload, prediction.predicted_score, at_risk
    )
    return ExplainResponse(
        prediction=prediction,
        method=raw["method"],
        algorithm=raw["algorithm"],
        explanations=raw["explanations"],
        contributions=[FeatureContribution(**c) for c in raw["contributions"]],
        top_feature=raw.get("top_feature"),
        summary=raw["explanations"][0] if raw["explanations"] else "",
    )


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(body: RecommendRequest | None = None):
    """
    Personalized recommendations + optional AI study plan.

    Rule-based + collaborative filtering.
    """
    req = body or RecommendRequest()
    rec = StudyPlannerService.generate_recommendations(req)
    plan = None
    if req.include_study_plan:
        plan = StudyPlannerService.daily_study_planner(req)
    return RecommendResponse(
        recommendations=rec.recommendations,
        weak_subjects=rec.weak_subjects,
        revision_order=rec.revision_order,
        collaborative_insights=rec.collaborative_insights,
        focus_message=rec.focus_message,
        study_plan=plan,
    )


@router.get("/analytics", response_model=AnalyticsAPIResponse)
async def analytics(
    performance_score: float = Query(82.0, ge=0, le=100),
    study_hours_week: float = Query(28.5, ge=0),
    study_streak_days: int = Query(14, ge=0),
    attendance_pct: float = Query(76.0, ge=0, le=100),
):
    """Analytics dashboard — cards, risk meter, chart series."""
    trend = [
        ChartPoint(label=f"W{i + 1}", value=float(v))
        for i, v in enumerate([68, 72, 75, 78, performance_score])
    ]
    subjects = [
        ChartPoint(label="Mathematics", value=91),
        ChartPoint(label="Programming", value=78),
        ChartPoint(label="Data Structures", value=62),
    ]
    return build_analytics(
        performance_score,
        trend,
        subjects,
        study_hours_week=study_hours_week,
        study_streak_days=study_streak_days,
        attendance_pct=attendance_pct,
    )


@router.get("/insights", response_model=InsightsResponse)
@ttl_cache(ttl_seconds=120, prefix="insights")
async def insights(
    study_hours: float = Query(3.0, ge=0, le=24),
    attendance_pct: float = Query(80.0, ge=0, le=100),
    sleep_hours: float = Query(7.0, ge=0, le=24),
    math_score: float = Query(58.0, ge=0, le=100),
):
    """AI insights — trends + cohort-backed messages."""
    req = InsightsRequest(
        study_hours=study_hours,
        attendance_pct=attendance_pct,
        sleep_hours=sleep_hours,
        previous_attendance_pct=attendance_pct - 12,
        subject_scores=[
            SubjectScoreInput(subject="Mathematics", score=math_score),
            SubjectScoreInput(subject="Portuguese", score=72.0),
            SubjectScoreInput(subject="Programming", score=78.0),
            SubjectScoreInput(subject="Data Structures", score=65.0),
        ],
    )
    return InsightsService.generate(req)


@router.get("/explain/global")
@ttl_cache(ttl_seconds=3600, prefix="explain_global")
async def explain_global():
    """Global SHAP feature rankings."""
    from app.models.explanation import GlobalExplainResponse, FeatureContribution

    data = get_explainer().global_importance()
    if not data:
        return GlobalExplainResponse(method="unavailable", algorithm="none", mean_abs_shap=[], plot_paths=[])
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
        plot_paths=["results/graphs/shap_summary.png", "results/graphs/shap_feature_importance.png"],
    )


@router.get("/ai/status", response_model=AIPlatformStatus)
@ttl_cache(ttl_seconds=30, prefix="ai_status")
async def ai_status():
    """Health of all Week 3 AI modules."""
    predictor = get_predictor()
    try:
        import shap  # noqa: F401

        shap_ok = True
    except ImportError:
        shap_ok = False

    return AIPlatformStatus(
        modules={
            "predict": "connected",
            "explain": "connected",
            "recommend": "connected",
            "analytics": "connected",
            "insights": "connected",
        },
        endpoints={
            "predict": "POST /predict",
            "recommend": "POST /recommend",
            "analytics": "GET /analytics",
            "insights": "GET /insights",
            "predict_explain": "POST /predict/explain",
        },
        models_loaded=predictor.is_loaded,
        shap_available=shap_ok,
    )
