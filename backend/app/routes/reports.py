"""Automated Report Generator routes (Week 7 · Day 4).

    GET  /api/reports/weekly/{user_id}         weekly report JSON + markdown
    GET  /api/reports/monthly/{user_id}        monthly report JSON + markdown
    POST /api/reports/weekly/{user_id}/pdf     generate & download PDF
    POST /api/reports/monthly/{user_id}/pdf    generate & download PDF
    POST /api/reports/weekly/{user_id}/email   email weekly report
    POST /api/reports/monthly/{user_id}/email  email monthly report
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models.reports import EmailReportResponse, MonthlyReportData, WeeklyReportData
from app.reports.service import ReportService
from app.services.user_service import UserService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/demo/weekly", response_model=WeeklyReportData)
async def demo_weekly(db: AsyncSession | None = Depends(get_optional_db)) -> WeeklyReportData:
    user = await UserService.get_demo_user(db)
    return await ReportService.weekly(user.id, db)


@router.get("/demo/monthly", response_model=MonthlyReportData)
async def demo_monthly(db: AsyncSession | None = Depends(get_optional_db)) -> MonthlyReportData:
    user = await UserService.get_demo_user(db)
    return await ReportService.monthly(user.id, db)


@router.get("/weekly/{user_id}", response_model=WeeklyReportData)
async def weekly_report(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> WeeklyReportData:
    return await ReportService.weekly(user_id, db)


@router.get("/monthly/{user_id}", response_model=MonthlyReportData)
async def monthly_report(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> MonthlyReportData:
    return await ReportService.monthly(user_id, db)


@router.post("/weekly/{user_id}/pdf")
async def weekly_pdf(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> FileResponse:
    try:
        saved = await ReportService.save_and_pdf(user_id, "weekly", db)
        if not saved.pdf_path:
            raise HTTPException(
                status_code=501,
                detail="PDF generation unavailable. Install fpdf2: pip install fpdf2",
            )
        return ReportService.pdf_file_response(saved.pdf_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/monthly/{user_id}/pdf")
async def monthly_pdf(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> FileResponse:
    try:
        saved = await ReportService.save_and_pdf(user_id, "monthly", db)
        if not saved.pdf_path:
            raise HTTPException(
                status_code=501,
                detail="PDF generation unavailable. Install fpdf2: pip install fpdf2",
            )
        return ReportService.pdf_file_response(saved.pdf_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/weekly/{user_id}/email", response_model=EmailReportResponse)
async def email_weekly(
    user_id: str,
    to_email: str | None = Query(None),
    db: AsyncSession | None = Depends(get_optional_db),
) -> EmailReportResponse:
    return await ReportService.email_report(user_id, "weekly", to_email, db)


@router.post("/monthly/{user_id}/email", response_model=EmailReportResponse)
async def email_monthly(
    user_id: str,
    to_email: str | None = Query(None),
    db: AsyncSession | None = Depends(get_optional_db),
) -> EmailReportResponse:
    return await ReportService.email_report(user_id, "monthly", to_email, db)
