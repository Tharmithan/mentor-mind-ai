"""User profile embeddings for similarity and routing (Week 7 · Day 1)."""

from __future__ import annotations

import json
import math
from pathlib import Path

from app.models.personalization import UnifiedUserProfile
from app.personalization.store import EMBEDDINGS_DIR, get_profile_store

EMBEDDING_DIM = 384


class UserEmbeddingService:
    @staticmethod
    def profile_to_text(profile: UnifiedUserProfile) -> str:
        weak = ", ".join(profile.weak_subjects) or "none"
        strong = ", ".join(profile.strong_subjects) or "none"
        interviews = (
            f"avg {profile.interview_avg_score:.0f}%"
            if profile.interview_avg_score is not None
            else "no sessions"
        )
        return (
            f"Student profile. Weak subjects: {weak}. Strong subjects: {strong}. "
            f"Learning style: {profile.learning_preferences.primary_style}. "
            f"Career goal: {profile.career_goal or 'undecided'}. "
            f"Interests: {', '.join(profile.interests) or 'general'}. "
            f"Interview performance: {interviews}. "
            f"Performance score: {profile.performance_score:.0f}."
        )

    @staticmethod
    def embed_profile(profile: UnifiedUserProfile) -> tuple[list[float], bool]:
        """Return embedding vector; uses SentenceTransformers when available."""
        text = UserEmbeddingService.profile_to_text(profile)
        try:
            from app.rag.embeddings import get_embedder

            vector = get_embedder().embed_one(text)
            get_profile_store().save_embedding(profile.user_id, vector, text)
            return vector, True
        except Exception:
            vector = UserEmbeddingService._fallback_vector(profile)
            get_profile_store().save_embedding(profile.user_id, vector, text)
            return vector, False

    @staticmethod
    def _fallback_vector(profile: UnifiedUserProfile) -> list[float]:
        """Deterministic feature hash when ML embedder unavailable."""
        import hashlib

        text = UserEmbeddingService.profile_to_text(profile)
        seed = hashlib.sha256(text.encode()).digest()
        vec = []
        for i in range(EMBEDDING_DIM):
            byte = seed[i % len(seed)]
            vec.append((byte / 255.0) * 2 - 1)
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na and nb else 0.0

    @staticmethod
    def find_similar(user_id: str, top_k: int = 3) -> list[tuple[str, float]]:
        store = get_profile_store()
        target = store.load_embedding(user_id)
        if target is None:
            return []

        results: list[tuple[str, float]] = []
        if not EMBEDDINGS_DIR.exists():
            return results

        for path in EMBEDDINGS_DIR.glob("*.json"):
            other_id = path.stem
            if other_id == user_id.replace("/", "_"):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                vec = data.get("vector")
                if vec:
                    sim = UserEmbeddingService.cosine_similarity(target, vec)
                    results.append((data.get("user_id", other_id), sim))
            except (json.JSONDecodeError, OSError):
                continue

        results.sort(key=lambda x: -x[1])
        return results[:top_k]
