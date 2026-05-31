"""Context retrieval from long-term memory (Week 7 · Day 2)."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.models.long_term_memory import ConversationMemoryEntry, LongTermMemory, MemoryContextResponse
from app.memory.progress import ProgressTracker


class ContextRetriever:
    @staticmethod
    def retrieve(
        memory: LongTermMemory,
        current_scores: dict[str, float],
        query: str | None = None,
        limit: int = 5,
    ) -> MemoryContextResponse:
        deltas = ProgressTracker.compute_deltas(memory, current_scores)
        insights = [d.insight for d in deltas[:4]]

        relevant = ContextRetriever._match_conversations(memory.conversations, query, limit)
        active_goal = next(
            (g.goal for g in reversed(memory.career_goals) if g.active),
            None,
        )
        interview_avg = ContextRetriever._recent_interview_avg(memory)

        summary_parts = [
            f"Long-term memory for user {memory.user_id}.",
            f"{len(memory.conversations)} conversations, {len(memory.subject_snapshots)} progress snapshots.",
        ]
        if active_goal:
            summary_parts.append(f"Active career goal: {active_goal}.")
        if insights:
            summary_parts.append(insights[0])

        return MemoryContextResponse(
            user_id=memory.user_id,
            summary=" ".join(summary_parts),
            progress_insights=insights,
            progress_deltas=deltas,
            relevant_conversations=relevant,
            active_career_goal=active_goal,
            recent_interview_avg=interview_avg,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _match_conversations(
        conversations: list[ConversationMemoryEntry],
        query: str | None,
        limit: int,
    ) -> list[ConversationMemoryEntry]:
        if not conversations:
            return []
        if not query:
            return list(reversed(conversations))[:limit]

        tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored: list[tuple[int, ConversationMemoryEntry]] = []
        for conv in conversations:
            text = f"{conv.summary} {' '.join(conv.topics)}".lower()
            score = sum(1 for t in tokens if t in text)
            if score:
                scored.append((score, conv))
        scored.sort(key=lambda x: -x[0])
        if scored:
            return [c for _, c in scored[:limit]]
        return list(reversed(conversations))[:limit]

    @staticmethod
    def _recent_interview_avg(memory: LongTermMemory) -> float | None:
        recent = memory.interview_scores[-5:]
        if not recent:
            return None
        return round(sum(r.overall for r in recent) / len(recent), 1)
