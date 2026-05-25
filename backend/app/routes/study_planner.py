from fastapi import APIRouter, Query

from app.models.study_plan import (
    DailyStudyPlannerResponse,
    PersonalizedRecommendationsRequest,
    PersonalizedRecommendationsResponse,
    SubjectScoreInput,
)
from app.services.study_planner_service import StudyPlannerService

router = APIRouter()


@router.post(
    "/recommendations/personalized",
    response_model=PersonalizedRecommendationsResponse,
)
async def personalized_recommendations(
    body: PersonalizedRecommendationsRequest | None = None,
):
    """
    Rule-based + collaborative filtering recommendations.

    Example: low math + low attendance → "Focus on Algebra revision this week."
    """
    return StudyPlannerService.generate_recommendations(body)


@router.get(
    "/recommendations/personalized",
    response_model=PersonalizedRecommendationsResponse,
)
async def personalized_recommendations_get(
    study_hours: float = Query(3.0, ge=0, le=24),
    attendance_pct: float = Query(80.0, ge=0, le=100),
    sleep_hours: float = Query(7.0, ge=0, le=24),
    math_score: float = Query(58.0, ge=0, le=100),
    portuguese_score: float = Query(72.0, ge=0, le=100),
):
    """GET variant with query params for quick dashboard use."""
    req = PersonalizedRecommendationsRequest(
        study_hours=study_hours,
        attendance_pct=attendance_pct,
        sleep_hours=sleep_hours,
        subject_scores=[
            SubjectScoreInput(subject="Mathematics", score=math_score),
            SubjectScoreInput(subject="Portuguese", score=portuguese_score),
            SubjectScoreInput(subject="Data Structures", score=62.0),
            SubjectScoreInput(subject="Programming", score=78.0),
        ],
    )
    return StudyPlannerService.generate_recommendations(req)


@router.post("/study-planner", response_model=DailyStudyPlannerResponse)
async def create_study_planner(body: PersonalizedRecommendationsRequest | None = None):
    """AI Daily Study Planner — timetable, revision priority, focus areas."""
    return StudyPlannerService.daily_study_planner(body)


@router.get("/study-planner", response_model=DailyStudyPlannerResponse)
async def get_study_planner(
    study_hours: float = Query(3.0, ge=0, le=24),
    attendance_pct: float = Query(75.0, ge=0, le=100),
    math_score: float = Query(58.0, ge=0, le=100),
):
    """Default demo plan (weak math, moderate attendance)."""
    req = PersonalizedRecommendationsRequest(
        study_hours=study_hours,
        attendance_pct=attendance_pct,
        subject_scores=[
            SubjectScoreInput(subject="Mathematics", score=math_score),
            SubjectScoreInput(subject="Portuguese", score=72.0),
            SubjectScoreInput(subject="Data Structures", score=62.0),
            SubjectScoreInput(subject="Programming", score=78.0),
        ],
    )
    return StudyPlannerService.daily_study_planner(req)
