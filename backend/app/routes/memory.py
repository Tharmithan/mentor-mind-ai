"""Long-Term Memory routes (Week 7 · Day 2).

    GET  /api/memory/{user_id}              full memory record
    GET  /api/memory/{user_id}/context      context retrieval for agents
    GET  /api/memory/{user_id}/progress     month-over-month progress
    POST /api/memory/{user_id}/sync         sync from chat/interview/plan stores
    POST /api/memory/{user_id}/snapshot     record subject score snapshot
    POST /api/memory/{user_id}/career-goal  record career goal
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.memory.service import LongTermMemoryService
from app.memory.store import get_memory_store
from app.models.long_term_memory import (
    LongTermMemory,
    MemoryContextResponse,
    MemoryProgressResponse,
)
from app.personalization.profile_engine import UserProfileEngine
from app.services.user_service import UserService

router = APIRouter(prefix="/memory", tags=["memory"])


async def _scores_for_user(user_id: str, db: AsyncSession | None) -> dict[str, float]:
    profile = await UserProfileEngine.get_or_build(user_id, db)
    return profile.subject_scores


@router.get("/demo/progress", response_model=MemoryProgressResponse)
async def demo_progress(
    db: AsyncSession | None = Depends(get_optional_db),
) -> MemoryProgressResponse:
    user = await UserService.get_demo_user(db)
    scores = await _scores_for_user(user.id, db)
    return LongTermMemoryService.get_progress(user.id, scores)


@router.get("/{user_id}", response_model=LongTermMemory)
async def get_memory(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> LongTermMemory:
    scores = await _scores_for_user(user_id, db)
    return LongTermMemoryService.sync_user(user_id, scores)


@router.get("/{user_id}/context", response_model=MemoryContextResponse)
async def get_memory_context(
    user_id: str,
    query: str | None = Query(None, description="Optional topic e.g. machine learning"),
    db: AsyncSession | None = Depends(get_optional_db),
) -> MemoryContextResponse:
    scores = await _scores_for_user(user_id, db)
    return LongTermMemoryService.get_context(user_id, scores, query=query)


@router.get("/{user_id}/progress", response_model=MemoryProgressResponse)
async def get_memory_progress(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> MemoryProgressResponse:
    scores = await _scores_for_user(user_id, db)
    return LongTermMemoryService.get_progress(user_id, scores)


@router.post("/{user_id}/sync", response_model=LongTermMemory)
async def sync_memory(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> LongTermMemory:
    scores = await _scores_for_user(user_id, db)
    return LongTermMemoryService.sync_user(user_id, scores)


@router.post("/{user_id}/snapshot", response_model=LongTermMemory)
async def record_snapshot(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> LongTermMemory:
    from app.memory.progress import ProgressTracker

    scores = await _scores_for_user(user_id, db)
    memory = get_memory_store().get_or_create(user_id)
    ProgressTracker.record_snapshot(memory, scores)
    get_memory_store().save(memory)
    return memory


@router.post("/{user_id}/career-goal")
async def record_career_goal(user_id: str, goal: str = Query(...)) -> dict:
    LongTermMemoryService.record_career_goal(user_id, goal)
    return {"message": "Career goal recorded", "goal": goal}
