"""Persist learning plans and track progress (Week 6 · Day 5)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.models.learning_planner import (
    CreateLearningPlanRequest,
    LearningPlanProgressUpdate,
    LearningPlanResponse,
    LearningRoadmapRequest,
    MilestoneStatus,
)
from app.planner.generator import RoadmapGenerator
from app.planner.weekly_planner import WeeklyPlanner

PLANS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "learning_plans"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PlanStore:
    def __init__(self) -> None:
        self._cache: dict[str, dict] = {}
        PLANS_DIR.mkdir(parents=True, exist_ok=True)

    def create(self, req: CreateLearningPlanRequest) -> LearningPlanResponse:
        roadmap = RoadmapGenerator.generate(
            LearningRoadmapRequest(goal=req.goal, hours_per_week=req.hours_per_week)
        )
        plan_id = uuid.uuid4().hex[:12]
        now = _now()
        data = {
            "plan_id": plan_id,
            "goal": req.goal,
            "career_title": roadmap.career_title,
            "progress_pct": 0.0,
            "current_month": 1,
            "current_week": 1,
            "hours_per_week": req.hours_per_week,
            "roadmap": roadmap.model_dump(),
            "milestones": [m.model_dump() for m in roadmap.milestones],
            "created_at": now,
            "updated_at": now,
            "user_id": req.user_id,
        }
        self._save(plan_id, data)
        return self._to_response(data)

    def get(self, plan_id: str) -> LearningPlanResponse | None:
        data = self._load(plan_id)
        return self._to_response(data) if data else None

    def update_progress(
        self, plan_id: str, body: LearningPlanProgressUpdate
    ) -> LearningPlanResponse | None:
        data = self._load(plan_id)
        if not data:
            return None

        if body.current_month is not None:
            data["current_month"] = body.current_month
        if body.current_week is not None:
            data["current_week"] = body.current_week
        if body.progress_pct is not None:
            data["progress_pct"] = body.progress_pct

        milestones = data.get("milestones", [])
        if body.milestone_id:
            for m in milestones:
                if m["id"] == body.milestone_id:
                    m["completed"] = True
                    m["completed_at"] = _now()
                    data["current_month"] = min(
                        m["month"] + 1,
                        data["roadmap"]["total_months"],
                    )
                    data["current_week"] = 1
            completed = sum(1 for m in milestones if m.get("completed"))
            total = len(milestones) or 1
            data["progress_pct"] = round(completed / total * 100, 1)

        data["updated_at"] = _now()
        self._save(plan_id, data)
        return self._to_response(data)

    def weekly_plan(self, plan_id: str) -> dict | None:
        data = self._load(plan_id)
        if not data:
            return None
        from app.models.learning_planner import LearningRoadmapResponse

        roadmap = LearningRoadmapResponse(**data["roadmap"])
        weekly = WeeklyPlanner.for_month(
            roadmap,
            month=data["current_month"],
            week=data["current_week"],
            progress_pct=data["progress_pct"],
        )
        weekly.plan_id = plan_id
        return {
            "plan": self._to_response(data).model_dump(),
            "weekly": weekly.model_dump(),
            "weekly_markdown": WeeklyPlanner.to_markdown(weekly),
        }

    def _load(self, plan_id: str) -> dict | None:
        if plan_id in self._cache:
            return self._cache[plan_id]
        path = PLANS_DIR / f"{plan_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        self._cache[plan_id] = data
        return data

    def _save(self, plan_id: str, data: dict) -> None:
        self._cache[plan_id] = data
        (PLANS_DIR / f"{plan_id}.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

    def _to_response(self, data: dict) -> LearningPlanResponse:
        from app.models.learning_planner import LearningRoadmapResponse

        return LearningPlanResponse(
            plan_id=data["plan_id"],
            goal=data["goal"],
            career_title=data["career_title"],
            progress_pct=data["progress_pct"],
            current_month=data["current_month"],
            current_week=data["current_week"],
            hours_per_week=data["hours_per_week"],
            roadmap=LearningRoadmapResponse(**data["roadmap"]),
            milestones=[MilestoneStatus(**m) for m in data["milestones"]],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


_store: PlanStore | None = None


def get_plan_store() -> PlanStore:
    global _store
    if _store is None:
        _store = PlanStore()
    return _store
