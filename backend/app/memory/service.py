"""Long-term memory orchestration (Week 7 · Day 2)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.memory.progress import ProgressTracker
from app.memory.retrieval import ContextRetriever
from app.memory.store import get_memory_store
from app.models.long_term_memory import (
    CareerGoalMemoryEntry,
    ConversationMemoryEntry,
    InterviewScoreMemoryEntry,
    LongTermMemory,
    MemoryContextResponse,
    MemoryProgressResponse,
    StudyPlanMemoryEntry,
)

INTERVIEW_DIR = Path(__file__).resolve().parents[2] / "uploads" / "interview_sessions"
AGENT_SESSIONS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "agent_sessions"
CHAT_SESSIONS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "sessions"


class LongTermMemoryService:
    @staticmethod
    def load(user_id: str) -> LongTermMemory:
        return get_memory_store().get_or_create(user_id)

    @staticmethod
    def sync_user(user_id: str, current_scores: dict[str, float] | None = None) -> LongTermMemory:
        """Pull data from file stores into long-term memory."""
        memory = get_memory_store().get_or_create(user_id)
        LongTermMemoryService._sync_interviews(memory)
        LongTermMemoryService._sync_agent_sessions(memory)
        LongTermMemoryService._sync_chat_sessions(memory)

        if current_scores:
            ProgressTracker.seed_baseline_if_empty(memory, current_scores)
            ProgressTracker.record_snapshot(memory, current_scores)

        get_memory_store().save(memory)
        return memory

    @staticmethod
    def get_context(
        user_id: str,
        current_scores: dict[str, float] | None = None,
        query: str | None = None,
    ) -> MemoryContextResponse:
        memory = LongTermMemoryService.sync_user(user_id, current_scores)
        scores = current_scores or LongTermMemoryService._latest_scores(memory)
        return ContextRetriever.retrieve(memory, scores, query=query)

    @staticmethod
    def get_progress(user_id: str, current_scores: dict[str, float] | None = None) -> MemoryProgressResponse:
        memory = LongTermMemoryService.sync_user(user_id, current_scores)
        scores = current_scores or LongTermMemoryService._latest_scores(memory)
        ProgressTracker.seed_baseline_if_empty(memory, scores)
        deltas = ProgressTracker.compute_deltas(memory, scores)
        get_memory_store().save(memory)

        baseline_label = memory.subject_snapshots[0].label if memory.subject_snapshots else "last month"
        return MemoryProgressResponse(
            user_id=user_id,
            deltas=deltas,
            narrative=ProgressTracker.narrative(deltas),
            snapshots_count=len(memory.subject_snapshots),
            month_comparison=baseline_label,
        )

    @staticmethod
    def record_agent_turn(
        user_id: str,
        session_id: str,
        message: str,
        answer: str,
        agent: str,
    ) -> None:
        memory = get_memory_store().get_or_create(user_id)
        summary = f"[{agent}] User: {message[:80]}… → {answer[:120]}…"
        topics = _extract_topics(message)
        memory.conversations.append(
            ConversationMemoryEntry(
                session_id=session_id,
                source="agent",
                summary=summary,
                topics=topics,
                agent=agent,
                recorded_at=datetime.now(timezone.utc).isoformat(),
            )
        )
        memory.conversations = memory.conversations[-50:]
        get_memory_store().save(memory)

    @staticmethod
    def record_career_goal(user_id: str, goal: str) -> None:
        memory = get_memory_store().get_or_create(user_id)
        for g in memory.career_goals:
            g.active = False
        memory.career_goals.append(
            CareerGoalMemoryEntry(
                goal=goal,
                recorded_at=datetime.now(timezone.utc).isoformat(),
                active=True,
            )
        )
        memory.career_goals = memory.career_goals[-10:]
        get_memory_store().save(memory)

    @staticmethod
    def record_study_plan(user_id: str, subject: str, summary: str, plan_id: str | None = None) -> None:
        memory = get_memory_store().get_or_create(user_id)
        memory.study_plans.append(
            StudyPlanMemoryEntry(
                plan_id=plan_id,
                subject=subject,
                summary=summary,
                recorded_at=datetime.now(timezone.utc).isoformat(),
            )
        )
        memory.study_plans = memory.study_plans[-20:]
        get_memory_store().save(memory)

    @staticmethod
    def record_interview_score(
        user_id: str,
        overall: float,
        session_id: str | None = None,
        technical: float | None = None,
        interview_type: str | None = None,
    ) -> None:
        memory = get_memory_store().get_or_create(user_id)
        memory.interview_scores.append(
            InterviewScoreMemoryEntry(
                session_id=session_id,
                overall=overall,
                technical=technical,
                interview_type=interview_type,
                recorded_at=datetime.now(timezone.utc).isoformat(),
            )
        )
        memory.interview_scores = memory.interview_scores[-30:]
        get_memory_store().save(memory)

    @staticmethod
    def _sync_interviews(memory: LongTermMemory) -> None:
        if not INTERVIEW_DIR.exists():
            return
        existing_ids = {e.session_id for e in memory.interview_scores if e.session_id}
        for path in sorted(INTERVIEW_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                sid = data.get("session_id")
                if sid in existing_ids:
                    continue
                summary = data.get("summary") or {}
                overall = summary.get("overall_score") or summary.get("overall")
                if overall is None:
                    continue
                memory.interview_scores.append(
                    InterviewScoreMemoryEntry(
                        session_id=sid,
                        overall=float(overall),
                        technical=_f(summary.get("technical_score") or summary.get("technical")),
                        communication=_f(summary.get("communication_score") or summary.get("communication")),
                        interview_type=data.get("interview_type"),
                        recorded_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
                    )
                )
                existing_ids.add(sid)
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                continue
        memory.interview_scores = memory.interview_scores[-30:]

    @staticmethod
    def _sync_agent_sessions(memory: LongTermMemory) -> None:
        if not AGENT_SESSIONS_DIR.exists():
            return
        existing = {(c.session_id, c.summary[:40]) for c in memory.conversations if c.source == "agent"}
        for path in sorted(AGENT_SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                sid = data.get("session_id", path.stem)
                for turn in data.get("turns", [])[-4:]:
                    if turn.get("role") != "user":
                        continue
                    content = turn.get("content", "")
                    key = (sid, content[:40])
                    if key in existing:
                        continue
                    memory.conversations.append(
                        ConversationMemoryEntry(
                            session_id=sid,
                            source="agent",
                            summary=f"User asked: {content[:100]}",
                            topics=_extract_topics(content),
                            agent=turn.get("agent"),
                            recorded_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
                        )
                    )
                    existing.add(key)
            except (json.JSONDecodeError, OSError):
                continue
        memory.conversations = memory.conversations[-50:]

    @staticmethod
    def _sync_chat_sessions(memory: LongTermMemory) -> None:
        if not CHAT_SESSIONS_DIR.exists():
            return
        existing = {(c.session_id, c.summary[:40]) for c in memory.conversations if c.source == "chat"}
        for path in sorted(CHAT_SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                sid = data.get("session_id", path.stem)
                topics = data.get("topics", [])
                if not topics:
                    continue
                summary = f"Chat topics: {', '.join(topics[-3:])}"
                key = (sid, summary[:40])
                if key in existing:
                    continue
                memory.conversations.append(
                    ConversationMemoryEntry(
                        session_id=sid,
                        source="chat",
                        summary=summary,
                        topics=topics[-5:],
                        recorded_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
                    )
                )
                existing.add(key)
            except (json.JSONDecodeError, OSError):
                continue

    @staticmethod
    def _latest_scores(memory: LongTermMemory) -> dict[str, float]:
        if memory.subject_snapshots:
            return memory.subject_snapshots[-1].scores
        from app.recommendation.engine import get_recommendation_engine

        return get_recommendation_engine().default_subject_scores()


def _extract_topics(text: str) -> list[str]:
    lower = text.lower()
    keywords = [
        "machine learning", "deep learning", "interview", "resume", "career",
        "python", "data structures", "exam", "study plan", "ai engineer",
    ]
    return [k.title() for k in keywords if k in lower]


def _f(val) -> float | None:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None
