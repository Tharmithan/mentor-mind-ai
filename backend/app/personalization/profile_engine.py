"""Unified user profile engine (Week 7 · Day 1)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.career.profile_builder import ProfileBuilder, parse_interests
from app.database.models import User
from app.models.personalization import (
    InterviewHistoryEntry,
    LearningPreferences,
    ProfileUpdateRequest,
    UnifiedUserProfile,
)
from app.personalization.embeddings import UserEmbeddingService
from app.personalization.preferences import LearningPreferenceTracker
from app.personalization.store import get_profile_store
from app.recommendation.engine import get_recommendation_engine

INTERVIEW_DIR = Path(__file__).resolve().parents[2] / "uploads" / "interview_sessions"
WEAK_THRESHOLD = 70.0
STRONG_THRESHOLD = 80.0


class UserProfileEngine:
    @staticmethod
    async def get_or_build(
        user_id: str,
        db: AsyncSession | None = None,
        refresh: bool = False,
    ) -> UnifiedUserProfile:
        store = get_profile_store()
        if not refresh:
            existing = store.get(user_id)
            if existing:
                return existing
        profile = await UserProfileEngine._build_from_sources(user_id, db)
        store.save(profile)
        return profile

    @staticmethod
    async def update(
        user_id: str,
        body: ProfileUpdateRequest,
        db: AsyncSession | None = None,
    ) -> UnifiedUserProfile:
        profile = await UserProfileEngine.get_or_build(user_id, db)
        if body.career_goal is not None:
            profile.career_goal = body.career_goal
        if body.interests is not None:
            profile.interests = body.interests
        if body.subject_scores is not None:
            profile.subject_scores.update(body.subject_scores)
            profile.weak_subjects, profile.strong_subjects = _split_subjects(
                profile.subject_scores
            )
        profile.updated_at = _now()
        profile.profile_summary = _build_summary(profile)
        get_profile_store().save(profile)
        return profile

    @staticmethod
    async def refresh_embedding(user_id: str, db: AsyncSession | None = None) -> tuple[UnifiedUserProfile, bool]:
        profile = await UserProfileEngine.get_or_build(user_id, db, refresh=True)
        _, used_ml = UserEmbeddingService.embed_profile(profile)
        profile.embedding_id = user_id
        profile.updated_at = _now()
        get_profile_store().save(profile)
        return profile, used_ml

    @staticmethod
    async def _build_from_sources(user_id: str, db: AsyncSession | None) -> UnifiedUserProfile:
        engine = get_recommendation_engine()
        subject_scores = dict(engine.default_subject_scores())
        email: str | None = None
        full_name = "Student"
        performance_score = 70.0
        study_hours = 10.0

        if db is not None:
            result = await db.execute(
                select(User)
                .options(selectinload(User.performance_data))
                .limit(1)
            )
            user = result.scalar_one_or_none()
            if user:
                email = user.email
                full_name = user.full_name or "Student"
                if user.performance_data:
                    subject_scores = {
                        p.subject: float(p.score) for p in user.performance_data
                    }
                    performance_score = sum(subject_scores.values()) / len(subject_scores)
                    study_hours = sum(float(p.study_hours or 0) for p in user.performance_data) or 10.0

        interview_history = _load_interview_history()
        interview_avg = _avg_interview(interview_history)

        career_profile = ProfileBuilder.build(
            subject_scores=subject_scores,
            interview_session_id=interview_history[0].session_id if interview_history else None,
        )

        weak, strong = _split_subjects(subject_scores)
        prefs = LearningPreferences(primary_style="interactive")

        stored = get_profile_store().get(user_id)
        if stored:
            prefs = stored.learning_preferences
            if stored.career_goal:
                career_goal = stored.career_goal
            else:
                career_goal = None
            interests = stored.interests or parse_interests(stored.career_goal)
        else:
            career_goal = None
            interests = list(career_profile.interests)

        profile = UnifiedUserProfile(
            user_id=user_id,
            email=email,
            full_name=full_name,
            subject_scores=subject_scores,
            weak_subjects=weak,
            strong_subjects=strong,
            learning_preferences=prefs,
            career_goal=career_goal,
            interests=interests,
            interview_history=interview_history,
            interview_avg_score=interview_avg,
            performance_score=round(performance_score, 1),
            study_hours_week=round(study_hours, 1),
            created_at=stored.created_at if stored else _now(),
            updated_at=_now(),
        )
        profile.profile_summary = _build_summary(profile)
        UserEmbeddingService.embed_profile(profile)
        profile.embedding_id = user_id
        return profile


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _split_subjects(scores: dict[str, float]) -> tuple[list[str], list[str]]:
    weak = [s for s, v in scores.items() if v < WEAK_THRESHOLD]
    strong = [s for s, v in scores.items() if v >= STRONG_THRESHOLD]
    if not weak and scores:
        weakest = min(scores, key=scores.get)  # type: ignore[arg-type]
        weak = [weakest]
    return weak, strong


def _load_interview_history() -> list[InterviewHistoryEntry]:
    if not INTERVIEW_DIR.exists():
        return []
    entries: list[InterviewHistoryEntry] = []
    for path in sorted(INTERVIEW_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            summary = data.get("summary") or {}
            entries.append(
                InterviewHistoryEntry(
                    session_id=data.get("session_id"),
                    overall_score=_f(summary.get("overall_score") or summary.get("overall")),
                    technical_score=_f(summary.get("technical_score") or summary.get("technical")),
                    communication_score=_f(summary.get("communication_score") or summary.get("communication")),
                    confidence_score=_f(summary.get("confidence_score") or summary.get("confidence")),
                    interview_type=data.get("interview_type"),
                    completed_at=data.get("updated_at"),
                )
            )
        except (json.JSONDecodeError, OSError):
            continue
    return entries


def _f(val) -> float | None:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _avg_interview(history: list[InterviewHistoryEntry]) -> float | None:
    scores = [h.overall_score for h in history if h.overall_score is not None]
    return round(sum(scores) / len(scores), 1) if scores else None


def _build_summary(profile: UnifiedUserProfile) -> str:
    style = profile.learning_preferences.primary_style
    weak = ", ".join(profile.weak_subjects[:3]) or "balanced"
    strong = ", ".join(profile.strong_subjects[:2]) or "general"
    return (
        f"{profile.full_name} — {style} learner. "
        f"Strong in {strong}; focus on {weak}. "
        f"Goal: {profile.career_goal or 'exploring careers'}."
    )
