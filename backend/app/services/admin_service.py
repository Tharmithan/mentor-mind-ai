"""Admin dashboard service (Week 8 · Bonus)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.predictor import get_predictor
from app.models.admin import AdminOverviewResponse, AdminUserSummary
from app.monitoring.service import MonitoringService
from app.database.models import User


class AdminService:
    @staticmethod
    async def overview(session: AsyncSession | None) -> AdminOverviewResponse:
        total_users = 0
        recent: list[AdminUserSummary] = []

        if session is not None:
            total_users = await session.scalar(select(func.count()).select_from(User)) or 0
            rows = await session.scalars(
                select(User).order_by(User.created_at.desc()).limit(5)
            )
            for u in rows.all():
                recent.append(
                    AdminUserSummary(
                        id=str(u.id),
                        email=u.email,
                        full_name=u.full_name or "Student",
                        role=u.role,
                        created_at=u.created_at.isoformat() if u.created_at else None,
                    )
                )
        else:
            total_users = 1
            recent = [
                AdminUserSummary(
                    id="demo-user-001",
                    email="student@mentormind.ai",
                    full_name="Demo Student",
                    role="student",
                )
            ]

        metrics = MonitoringService.model_metrics()
        feedback = MonitoringService.user_feedback("demo-user-001")
        sat = MonitoringService.satisfaction("demo-user-001")

        predictor = get_predictor()
        prod_version = predictor._version if predictor.is_loaded else None

        doc_count = 0
        try:
            from app.rag.document_service import DocumentService

            doc_count = DocumentService.list_documents().count
        except Exception:
            pass

        interview_sessions = 0
        try:
            from app.interview.session import get_session_store

            interview_sessions = len(get_session_store()._cache)
        except Exception:
            pass

        return AdminOverviewResponse(
            total_users=total_users,
            total_predictions=metrics.total_predictions,
            total_feedback=len(feedback),
            models_loaded=predictor.is_loaded,
            production_model_version=prod_version,
            vector_documents=doc_count,
            active_interview_sessions=interview_sessions,
            avg_satisfaction=sat.avg_rating if sat.total_feedback else None,
            recent_users=recent,
            system_status={
                "api": "healthy",
                "database": "connected" if session is not None else "demo_mode",
                "ml_models": "loaded" if predictor.is_loaded else "unavailable",
            },
        )
