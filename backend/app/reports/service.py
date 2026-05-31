"""Report orchestration — generate, persist, PDF, email (Week 7 · Day 4)."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reports import (
    EmailReportResponse,
    MonthlyReportData,
    ReportFileResponse,
    WeeklyReportData,
)
from app.reports.email_sender import send_report_email
from app.reports.generator import ReportGenerator
from app.reports.pdf_exporter import markdown_to_pdf

REPORTS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "reports"


class ReportService:
    @staticmethod
    async def weekly(user_id: str, db: AsyncSession | None = None) -> WeeklyReportData:
        return await ReportGenerator.weekly(user_id, db)

    @staticmethod
    async def monthly(user_id: str, db: AsyncSession | None = None) -> MonthlyReportData:
        return await ReportGenerator.monthly(user_id, db)

    @staticmethod
    async def save_and_pdf(
        user_id: str,
        report_type: str,
        db: AsyncSession | None = None,
    ) -> ReportFileResponse:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_id = uuid.uuid4().hex[:10]
        now = datetime.now(timezone.utc).isoformat()

        if report_type == "monthly":
            data = await ReportGenerator.monthly(user_id, db)
            md = data.markdown
            title = "MentorMind Monthly Report"
        else:
            data = await ReportGenerator.weekly(user_id, db)
            md = data.markdown
            title = "MentorMind Weekly Report"

        md_path = REPORTS_DIR / f"{report_id}_{report_type}.md"
        pdf_path = REPORTS_DIR / f"{report_id}_{report_type}.pdf"
        md_path.write_text(md, encoding="utf-8")

        pdf_ok = markdown_to_pdf(md, pdf_path, title=title)
        return ReportFileResponse(
            report_id=report_id,
            report_type=report_type,
            user_id=user_id,
            markdown_path=str(md_path),
            pdf_path=str(pdf_path) if pdf_ok else None,
            generated_at=now,
        )

    @staticmethod
    def pdf_file_response(pdf_path: str) -> FileResponse:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError("PDF not found")
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=path.name,
        )

    @staticmethod
    async def email_report(
        user_id: str,
        report_type: str,
        to_email: str | None,
        db: AsyncSession | None = None,
    ) -> EmailReportResponse:
        saved = await ReportService.save_and_pdf(user_id, report_type, db)
        if report_type == "monthly":
            data = await ReportGenerator.monthly(user_id, db)
            subject = f"MentorMind AI — Monthly Report ({data.period_label})"
        else:
            data = await ReportGenerator.weekly(user_id, db)
            subject = f"MentorMind AI — Weekly Report ({data.period_label})"

        recipient = to_email or os.getenv("REPORT_EMAIL_TO")
        if not recipient:
            return EmailReportResponse(
                sent=False,
                message="No recipient. Set REPORT_EMAIL_TO in .env or pass to_email.",
            )

        pdf_path = Path(saved.pdf_path) if saved.pdf_path else None
        sent, message = send_report_email(
            recipient,
            subject,
            data.markdown,
            pdf_path=pdf_path if pdf_path and pdf_path.exists() else None,
        )
        return EmailReportResponse(sent=sent, message=message, to_email=recipient if sent else None)
