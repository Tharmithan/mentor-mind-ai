"""Long-term memory JSON store (Week 7 · Day 2)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.models.long_term_memory import LongTermMemory

MEMORY_DIR = Path(__file__).resolve().parents[2] / "uploads" / "long_term_memory"


class LongTermMemoryStore:
    def __init__(self) -> None:
        self._cache: dict[str, LongTermMemory] = {}
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id: str) -> Path:
        safe = user_id.replace("/", "_")
        return MEMORY_DIR / f"{safe}.json"

    def get(self, user_id: str) -> LongTermMemory | None:
        if user_id in self._cache:
            return self._cache[user_id]
        path = self._path(user_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        mem = LongTermMemory(**data)
        self._cache[user_id] = mem
        return mem

    def get_or_create(self, user_id: str) -> LongTermMemory:
        existing = self.get(user_id)
        if existing:
            return existing
        now = datetime.now(timezone.utc).isoformat()
        mem = LongTermMemory(user_id=user_id, created_at=now, updated_at=now)
        self.save(mem)
        return mem

    def save(self, memory: LongTermMemory) -> None:
        memory.updated_at = datetime.now(timezone.utc).isoformat()
        self._cache[memory.user_id] = memory
        self._path(memory.user_id).write_text(
            memory.model_dump_json(indent=2), encoding="utf-8"
        )


_store: LongTermMemoryStore | None = None


def get_memory_store() -> LongTermMemoryStore:
    global _store
    if _store is None:
        _store = LongTermMemoryStore()
    return _store
