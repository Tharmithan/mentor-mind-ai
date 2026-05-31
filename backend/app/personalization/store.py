"""JSON persistence for user profiles (Week 7 · Day 1)."""

from __future__ import annotations

import json
from pathlib import Path

from app.models.personalization import UnifiedUserProfile

PROFILES_DIR = Path(__file__).resolve().parents[2] / "uploads" / "user_profiles"
EMBEDDINGS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "user_embeddings"


class ProfileStore:
    def __init__(self) -> None:
        self._cache: dict[str, UnifiedUserProfile] = {}
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id: str) -> Path:
        safe = user_id.replace("/", "_")
        return PROFILES_DIR / f"{safe}.json"

    def get(self, user_id: str) -> UnifiedUserProfile | None:
        if user_id in self._cache:
            return self._cache[user_id]
        path = self._path(user_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = UnifiedUserProfile(**data)
        self._cache[user_id] = profile
        return profile

    def save(self, profile: UnifiedUserProfile) -> None:
        self._cache[profile.user_id] = profile
        self._path(profile.user_id).write_text(
            profile.model_dump_json(indent=2), encoding="utf-8"
        )

    def save_embedding(self, user_id: str, vector: list[float], text: str) -> None:
        safe = user_id.replace("/", "_")
        payload = {"user_id": user_id, "vector": vector, "text": text}
        (EMBEDDINGS_DIR / f"{safe}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def load_embedding(self, user_id: str) -> list[float] | None:
        safe = user_id.replace("/", "_")
        path = EMBEDDINGS_DIR / f"{safe}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("vector")

    def list_embedding_user_ids(self) -> list[str]:
        if not EMBEDDINGS_DIR.exists():
            return []
        return [p.stem for p in EMBEDDINGS_DIR.glob("*.json")]


_store: ProfileStore | None = None


def get_profile_store() -> ProfileStore:
    global _store
    if _store is None:
        _store = ProfileStore()
    return _store
