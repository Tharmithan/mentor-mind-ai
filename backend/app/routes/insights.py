from fastapi import APIRouter, Query

from app.models.insights import InsightsReportResponse, InsightsRequest, InsightsResponse
from app.services.insights_service import InsightsService

router = APIRouter()


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    study_hours: float = Query(3.0, ge=0, le=24),
    attendance_pct: float = Query(80.0, ge=0, le=100),
    sleep_hours: float = Query(7.0, ge=0, le=24),
    previous_attendance_pct: float | None = Query(None, ge=0, le=100),
    math_score: float = Query(58.0, ge=0, le=100),
):
    """AI insights with trend analysis (demo: attendance drop vs last month)."""
    from app.models.study_plan import SubjectScoreInput

    req = InsightsRequest(
        study_hours=study_hours,
        attendance_pct=attendance_pct,
        sleep_hours=sleep_hours,
        previous_attendance_pct=previous_attendance_pct or attendance_pct - 12,
        subject_scores=[
            SubjectScoreInput(subject="Mathematics", score=math_score),
            SubjectScoreInput(subject="Portuguese", score=72.0),
            SubjectScoreInput(subject="Programming", score=78.0),
            SubjectScoreInput(subject="Data Structures", score=65.0),
        ],
        previous_subject_scores=[
            SubjectScoreInput(subject="Programming", score=72.0),
            SubjectScoreInput(subject="Data Structures", score=60.0),
            SubjectScoreInput(subject="Mathematics", score=math_score - 2),
        ],
    )
    return InsightsService.generate(req)


@router.post("/insights/generate", response_model=InsightsResponse)
async def post_insights(body: InsightsRequest | None = None):
    """Generate personalized AI insights from student profile."""
    return InsightsService.generate(body)


@router.get("/insights/summary", response_model=InsightsResponse)
async def performance_summary():
    """Performance summary + highlights only (full insights payload)."""
    return InsightsService.generate()


@router.post("/insights/report", response_model=InsightsReportResponse)
async def insights_report(body: InsightsRequest | None = None):
    """
    Natural language report — uses LLM when OPENAI_API_KEY is set,
    otherwise template-based analytics narrative.
    """
    return await InsightsService.generate_report(body)


@router.get("/insights/report", response_model=InsightsReportResponse)
async def get_insights_report():
    return await InsightsService.generate_report()
