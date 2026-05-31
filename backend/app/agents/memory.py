"""Agent memory — session state + routing history (Week 6 · Day 1).

Extends conversation memory with agent-specific context:
  - which agent handled each turn
  - user goals / document focus
  - cross-agent session continuity
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

AGENT_SESSIONS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "agent_sessions"


@dataclass
class AgentTurn:
    role: str
    content: str
    agent: str | None = None

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content, "agent": self.agent}


@dataclass
class AgentSession:
    session_id: str
    turns: list[AgentTurn] = field(default_factory=list)
    last_agent: str | None = None
    routing_log: list[dict] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_user(self, text: str) -> None:
        self.turns.append(AgentTurn(role="user", content=text))
        self._trim()
        self._touch()

    def add_assistant(self, text: str, agent: str) -> None:
        self.turns.append(AgentTurn(role="assistant", content=text, agent=agent))
        self.last_agent = agent
        self._trim()
        self._touch()

    def log_route(self, agent: str, confidence: float, reason: str) -> None:
        self.routing_log.append(
            {"agent": agent, "confidence": confidence, "reason": reason, "at": self.updated_at}
        )
        self.routing_log = self.routing_log[-20:]

    def history(self, limit: int = 10) -> list[dict]:
        return [t.to_dict() for t in self.turns[-limit:]]

    def buffer_for_llm(self, limit: int = 8) -> list[dict]:
        return [{"role": t.role, "content": t.content} for t in self.turns[-limit:]]

    def _trim(self) -> None:
        if len(self.turns) > 40:
            self.turns = self.turns[-40:]

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turns": [t.to_dict() for t in self.turns],
            "last_agent": self.last_agent,
            "routing_log": self.routing_log,
            "context": self.context,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentSession":
        s = cls(session_id=data["session_id"])
        s.last_agent = data.get("last_agent")
        s.routing_log = data.get("routing_log", [])
        s.context = data.get("context", {})
        s.created_at = data.get("created_at", s.created_at)
        s.updated_at = data.get("updated_at", s.updated_at)
        for t in data.get("turns", []):
            s.turns.append(AgentTurn(role=t["role"], content=t["content"], agent=t.get("agent")))
        return s


class AgentMemoryStore:
    """In-process + JSON persistence for agent sessions."""

    def __init__(self) -> None:
        self._cache: dict[str, AgentSession] = {}
        AGENT_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def create(self) -> AgentSession:
        session = AgentSession(session_id=uuid.uuid4().hex[:12])
        self._cache[session.session_id] = session
        self._persist(session)
        return session

    def get_or_create(self, session_id: str | None) -> AgentSession:
        if session_id and session_id in self._cache:
            return self._cache[session_id]
        path = AGENT_SESSIONS_DIR / f"{session_id}.json" if session_id else None
        if session_id and path and path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            session = AgentSession.from_dict(data)
            self._cache[session_id] = session
            return session
        if session_id:
            session = AgentSession(session_id=session_id)
            self._cache[session_id] = session
            return session
        return self.create()

    def save(self, session: AgentSession) -> None:
        self._cache[session.session_id] = session
        self._persist(session)

    def _persist(self, session: AgentSession) -> None:
        (AGENT_SESSIONS_DIR / f"{session.session_id}.json").write_text(
            json.dumps(session.to_dict(), indent=2), encoding="utf-8"
        )

    def get(self, session_id: str) -> AgentSession | None:
        if session_id in self._cache:
            return self._cache[session_id]
        path = AGENT_SESSIONS_DIR / f"{session_id}.json"
        if not path.exists():
            return None
        session = AgentSession.from_dict(json.loads(path.read_text(encoding="utf-8")))
        self._cache[session_id] = session
        return session


_store: AgentMemoryStore | None = None


def get_agent_memory() -> AgentMemoryStore:
    global _store
    if _store is None:
        _store = AgentMemoryStore()
    return _store
