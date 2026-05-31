"""Shared memory workspace for multi-agent collaboration (Week 6 · Day 6)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.agents.memory import AgentSession


class SharedMemory:
    """Cross-agent workspace attached to an agent session."""

    def __init__(self, session: AgentSession) -> None:
        self.session = session
        if "shared" not in session.context:
            session.context["shared"] = {
                "career_goal": None,
                "career_id": None,
                "skill_gaps": [],
                "study_focus": [],
                "interview_topics": [],
                "resume_suggestions": [],
                "messages": [],
            }
        self.data: dict = session.context["shared"]

    def set(self, key: str, value) -> None:
        self.data[key] = value

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def post_message(self, from_agent: str, to_agent: str, content: str) -> None:
        """Record inter-agent communication."""
        msgs = self.data.setdefault("messages", [])
        msgs.append(
            {
                "from": from_agent,
                "to": to_agent,
                "content": content,
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.data["messages"] = msgs[-30:]

    def to_dict(self) -> dict:
        return dict(self.data)
