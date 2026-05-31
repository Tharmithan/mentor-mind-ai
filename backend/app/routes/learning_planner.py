"""Personalized Learning Planner routes (Week 6 · Day 5).

    POST /api/learning-planner/roadmap       generate monthly roadmap (no persist)
    POST /api/learning-planner/plans         create plan + milestones
    GET  /api/learning-planner/plans/{id}    get plan + progress
    PATCH /api/learning-planner/plans/{id}/progress  update milestones / week
    GET  /api/learning-planner/plans/{id}/weekly     weekly breakdown
"""

from fastapi import APIRouter, HTTPException

from app.models.learning_planner import (
    CreateLearningPlanRequest,
    LearningPlanProgressUpdate,
    LearningPlanResponse,
    LearningRoadmapRequest,
    LearningRoadmapResponse,
    WeeklyPlanResponse,
)
from app.planner.generator import RoadmapGenerator
from app.planner.progress_store import get_plan_store

router = APIRouter(prefix="/learning-planner", tags=["learning-planner"])


@router.post("/roadmap", response_model=LearningRoadmapResponse)
async def generate_roadmap(body: LearningRoadmapRequest) -> LearningRoadmapResponse:
    return RoadmapGenerator.generate(body)


@router.post("/plans", response_model=LearningPlanResponse)
async def create_plan(body: CreateLearningPlanRequest) -> LearningPlanResponse:
    return get_plan_store().create(body)


@router.get("/plans/{plan_id}", response_model=LearningPlanResponse)
async def get_plan(plan_id: str) -> LearningPlanResponse:
    plan = get_plan_store().get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    return plan


@router.patch("/plans/{plan_id}/progress", response_model=LearningPlanResponse)
async def update_progress(
    plan_id: str, body: LearningPlanProgressUpdate
) -> LearningPlanResponse:
    plan = get_plan_store().update_progress(plan_id, body)
    if plan is None:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    return plan


@router.get("/plans/{plan_id}/weekly")
async def get_weekly_plan(plan_id: str) -> dict:
    result = get_plan_store().weekly_plan(plan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    return result
