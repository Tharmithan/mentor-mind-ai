"""Learning goal tracker — persist goals per agent session (Week 6 · Day 2)."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.models.study_tutor import LearningGoal, LearningGoalCreate, LearningGoalUpdate

GOALS_DIR = Path(__file__).resolve().parents[3] / "uploads" / "study_goals"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GoalTracker:
    def __init__(self) -> None:
        self._cache: dict[str, list[LearningGoal]] = {}
        GOALS_DIR.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return GOALS_DIR / f"{session_id}.json"

    def list_goals(self, session_id: str) -> list[LearningGoal]:
        if session_id in self._cache:
            return self._cache[session_id]
        path = self._path(session_id)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        goals = [LearningGoal(**g) for g in data.get("goals", [])]
        self._cache[session_id] = goals
        return goals

    def create_goal(self, session_id: str, body: LearningGoalCreate) -> LearningGoal:
        goals = self.list_goals(session_id)
        goal = LearningGoal(
            id=uuid.uuid4().hex[:10],
            title=body.title,
            subject=body.subject,
            target_days=body.target_days,
            target_date=body.target_date,
            progress_pct=0,
            created_at=_now(),
            updated_at=_now(),
        )
        goals.append(goal)
        self._save(session_id, goals)
        return goal

    def update_goal(
        self, session_id: str, goal_id: str, body: LearningGoalUpdate
    ) -> LearningGoal | None:
        goals = self.list_goals(session_id)
        for i, g in enumerate(goals):
            if g.id != goal_id:
                continue
            updated = g.model_copy(deep=True)
            if body.progress_pct is not None:
                updated.progress_pct = body.progress_pct
            if body.completed_milestone:
                if body.completed_milestone not in updated.milestones_completed:
                    updated.milestones_completed.append(body.completed_milestone)
                updated.progress_pct = min(
                    100,
                    updated.progress_pct + max(5, 100 // max(updated.target_days or 10, 1)),
                )
            if body.note:
                updated.notes.append(body.note)
            updated.updated_at = _now()
            goals[i] = updated
            self._save(session_id, goals)
            return updated
        return None

    def _save(self, session_id: str, goals: list[LearningGoal]) -> None:
        self._cache[session_id] = goals
        self._path(session_id).write_text(
            json.dumps({"session_id": session_id, "goals": [g.model_dump() for g in goals]}, indent=2),
            encoding="utf-8",
        )

    def parse_goal_from_message(self, message: str) -> LearningGoalCreate | None:
        lower = message.lower()
        if not re.search(r"\b(goal|track|learning target|i want to learn)\b", lower):
            return None
        days_m = re.search(r"(\d+)\s*days?", lower)
        target_days = int(days_m.group(1)) if days_m else 30
        subject = "General"
        for alias in ("machine learning", "python", "data structures", "programming", "math"):
            if alias in lower:
                subject = alias.title() if alias != "machine learning" else "Machine Learning"
                break
        title_m = re.search(r"(?:learn|master|study)\s+([a-z][a-z\s]{2,25}?)(?:\s+in|\s+for|$)", lower)
        if title_m:
            subj_raw = title_m.group(1).strip()
            subject = subj_raw.title()
            title = f"Learn {subject}"
        else:
            title = f"Study {subject}"
        return LearningGoalCreate(title=title, subject=subject, target_days=target_days)

    def parse_progress_update(self, message: str) -> tuple[str | None, float | None, str | None]:
        """Return (goal_id_hint, progress_pct, milestone)."""
        lower = message.lower()
        if not re.search(r"\b(progress|completed|finished|done|milestone|day \d+)\b", lower):
            return None, None, None
        pct_m = re.search(r"(\d+)\s*%", message)
        progress = float(pct_m.group(1)) if pct_m else None
        day_m = re.search(r"(?:completed|finished)\s+day\s+(\d+)", lower)
        milestone = f"Day {day_m.group(1)}" if day_m else None
        return None, progress, milestone


_tracker: GoalTracker | None = None


def get_goal_tracker() -> GoalTracker:
    global _tracker
    if _tracker is None:
        _tracker = GoalTracker()
    return _tracker
