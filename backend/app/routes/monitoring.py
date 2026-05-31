"""Monitoring & Feedback Loop routes (Week 7 · Day 6).

    POST /api/monitoring/feedback              submit rating / comment
    GET  /api/monitoring/feedback/{user_id}    user feedback history
    GET  /api/monitoring/satisfaction/{user_id}  satisfaction summary
    GET  /api/monitoring/model-metrics         prediction monitoring
    GET  /api/monitoring/improvements/{user_id}  continuous improvement insights
    GET  /api/monitoring/dashboard/{user_id}     full monitoring dashboard
    GET  /api/monitoring/demo                    demo user dashboard
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import get_optional_db
from app.models.monitoring import (
    FeedbackEntry,
    FeedbackSubmitRequest,
    ImprovementLoopResponse,
    ModelMonitoringMetrics,
    MonitoringDashboard,
    SatisfactionSummary,
)
from app.monitoring.service import MonitoringService
from app.services.user_service import UserService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


async def _default_user_id(db) -> str:
    user = await UserService.get_demo_user(db)
    return user.id


@router.post("/feedback", response_model=FeedbackEntry)
async def submit_feedback(body: FeedbackSubmitRequest) -> FeedbackEntry:
    return MonitoringService.submit_feedback(body)


@router.get("/feedback/{user_id}", response_model=list[FeedbackEntry])
async def list_feedback(user_id: str) -> list[FeedbackEntry]:
    return MonitoringService.user_feedback(user_id)


@router.get("/satisfaction/{user_id}", response_model=SatisfactionSummary)
async def get_satisfaction(user_id: str) -> SatisfactionSummary:
    return MonitoringService.satisfaction(user_id)


@router.get("/model-metrics", response_model=ModelMonitoringMetrics)
async def get_model_metrics() -> ModelMonitoringMetrics:
    return MonitoringService.model_metrics()


@router.get("/improvements/{user_id}", response_model=ImprovementLoopResponse)
async def get_improvements(user_id: str) -> ImprovementLoopResponse:
    return MonitoringService.improvements(user_id)


@router.get("/dashboard/{user_id}", response_model=MonitoringDashboard)
async def get_dashboard(user_id: str) -> MonitoringDashboard:
    return MonitoringService.dashboard(user_id)


@router.get("/demo", response_model=MonitoringDashboard)
async def demo_dashboard(db=Depends(get_optional_db)) -> MonitoringDashboard:
    user_id = await _default_user_id(db)
    return MonitoringService.dashboard(user_id)
