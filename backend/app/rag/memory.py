"""Conversation memory for the AI tutor (Week 4 · Day 6).

Gives the chatbot short-term memory so follow-ups work:

    User: "Explain CNN."      ->  AI explains CNNs
    User: "Give an example."  ->  AI knows "an example of a CNN"

Built on LangChain's ``InMemoryChatMessageHistory`` (the ConversationBufferMemory
primitive) per session, with JSON persistence to ``backend/uploads/sessions/`` so a
conversation survives restarts. It also tracks "previous learning context" — the recent
topics and the document a session has been studying.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.chat_history import InMemoryChatMessageHistory

# backend/app/rag/memory.py -> parents[2] == backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]
SESSIONS_DIR = BACKEND_DIR / "uploads" / "sessions"

MAX_TURNS = 20  # cap stored turns per session (buffer window)


class Session:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.history = InMemoryChatMessageHistory()
        self.topics: list[str] = []          # recent user questions (learning context)
        self.last_document_id: str | None = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at

    # --- mutation -------------------------------------------------------- #
    def add_user(self, text: str, document_id: str | None = None) -> None:
        self.history.add_user_message(text)
        self.topics.append(text)
        self.topics = self.topics[-6:]
        if document_id:
            self.last_document_id = document_id
        self._touch_and_trim()

    def add_ai(self, text: str) -> None:
        self.history.add_ai_message(text)
        self._touch_and_trim()

    def _touch_and_trim(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()
        msgs = self.history.messages
        if len(msgs) > MAX_TURNS * 2:
            self.history.messages = msgs[-MAX_TURNS * 2 :]

    # --- views ----------------------------------------------------------- #
    def buffer(self, limit: int | None = None) -> list[dict]:
        """ConversationBufferMemory-style list of {role, content}."""
        out = [
            {"role": "user" if m.type == "human" else "assistant", "content": m.content}
            for m in self.history.messages
        ]
        return out[-limit:] if limit else out

    def recent_topic(self) -> str | None:
        """The previous user question (used to resolve follow-up references)."""
        return self.topics[-2] if len(self.topics) >= 2 else None

    # --- persistence ----------------------------------------------------- #
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "messages": self.buffer(),
            "topics": self.topics,
            "last_document_id": self.last_document_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        s = cls(data["session_id"])
        for m in data.get("messages", []):
            if m["role"] == "user":
                s.history.add_user_message(m["content"])
            else:
                s.history.add_ai_message(m["content"])
        s.topics = data.get("topics", [])
        s.last_document_id = data.get("last_document_id")
        s.created_at = data.get("created_at", s.created_at)
        s.updated_at = data.get("updated_at", s.updated_at)
        return s


class ConversationMemory:
    """In-process session store backed by JSON files on disk."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def create(self) -> Session:
        session = Session(uuid.uuid4().hex[:12])
        self._sessions[session.session_id] = session
        self._persist(session)
        return session

    def get(self, session_id: str) -> Session | None:
        if session_id in self._sessions:
            return self._sessions[session_id]
        path = SESSIONS_DIR / f"{session_id}.json"
        if path.exists():
            session = Session.from_dict(json.loads(path.read_text(encoding="utf-8")))
            self._sessions[session_id] = session
            return session
        return None

    def get_or_create(self, session_id: str | None) -> Session:
        if session_id:
            existing = self.get(session_id)
            if existing:
                return existing
        return self.create()

    def save(self, session: Session) -> None:
        self._persist(session)

    def delete(self, session_id: str) -> bool:
        self._sessions.pop(session_id, None)
        path = SESSIONS_DIR / f"{session_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def _persist(self, session: Session) -> None:
        (SESSIONS_DIR / f"{session.session_id}.json").write_text(
            json.dumps(session.to_dict(), indent=2), encoding="utf-8"
        )


_memory: ConversationMemory | None = None


def get_memory() -> ConversationMemory:
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
