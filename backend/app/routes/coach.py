"""AI Coach Dashboard routes (Week 6 · Day 7).

    GET /api/coach/overview       scores, charts, skill gaps, recommendations, weekly report
    GET /api/coach/weekly-report  standalone weekly progress report
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models.coach import CoachOverviewResponse, WeeklyProgressReport
from app.services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["coach"])


@router.get("/overview", response_model=CoachOverviewResponse)
async def coach_overview(
    target_career: str | None = Query(None, description="Target role e.g. AI Engineer"),
    session_id: str | None = Query(None, description="Agent session for goal tracking"),
    interview_session_id: str | None = Query(None),
    db: AsyncSession | None = Depends(get_optional_db),
) -> CoachOverviewResponse:
    return await CoachService.get_overview(
        db,
        target_career=target_career,
        session_id=session_id,
        interview_session_id=interview_session_id,
    )


@router.get("/weekly-report", response_model=WeeklyProgressReport)
async def coach_weekly_report(
    session_id: str | None = Query(None),
    target_career: str | None = Query(None),
    db: AsyncSession | None = Depends(get_optional_db),
) -> WeeklyProgressReport:
    overview = await CoachService.get_overview(db, target_career=target_career, session_id=session_id)
    return overview.weekly_report
