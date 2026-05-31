"""Collect user ratings and qualitative feedback (Week 7 · Day 6)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.models.monitoring import FeedbackEntry, FeedbackSubmitRequest
from app.monitoring.store import get_monitoring_store


class FeedbackCollector:
    @staticmethod
    def submit(req: FeedbackSubmitRequest) -> FeedbackEntry:
        helpful = req.helpful if req.helpful is not None else req.rating >= 4
        entry = FeedbackEntry(
            feedback_id=uuid.uuid4().hex[:12],
            user_id=req.user_id,
            category=req.category,
            target_id=req.target_id or req.comment[:40] or "unspecified",
            rating=req.rating,
            helpful=helpful,
            comment=req.comment.strip(),
            metadata=req.metadata,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        store = get_monitoring_store()
        entries = store.load_feedback()
        entries.append(entry.model_dump())
        store.save_feedback(entries[-500:])
        return entry

    @staticmethod
    def list_for_user(user_id: str, limit: int = 50) -> list[FeedbackEntry]:
        store = get_monitoring_store()
        items = [e for e in store.load_feedback() if e.get("user_id") == user_id]
        return [FeedbackEntry(**e) for e in reversed(items[-limit:])]

    @staticmethod
    def list_all(limit: int = 100) -> list[FeedbackEntry]:
        store = get_monitoring_store()
        items = store.load_feedback()
        return [FeedbackEntry(**e) for e in reversed(items[-limit:])]

    @staticmethod
    def negative_targets(user_id: str, category: str | None = None) -> list[str]:
        """Targets with rating <= 2 or not helpful — used by improvement loop."""
        store = get_monitoring_store()
        bad: dict[str, int] = {}
        for e in store.load_feedback():
            if e.get("user_id") != user_id:
                continue
            if category and e.get("category") != category:
                continue
            if e.get("rating", 5) <= 2 or not e.get("helpful", True):
                tid = e.get("target_id", "")
                if tid:
                    bad[tid] = bad.get(tid, 0) + 1
        return [k for k, v in bad.items() if v >= 1]
