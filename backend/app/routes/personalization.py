"""User Personalization Engine routes (Week 7 · Day 1).

    GET   /api/personalization/profile/{user_id}     unified user profile
    POST  /api/personalization/profile/build         rebuild profile + embedding
    PATCH /api/personalization/profile/{user_id}     update career/goals/scores
    PATCH /api/personalization/preferences/{user_id} update learning style
    GET   /api/personalization/recommendations/{user_id}  style-aware recs
    GET   /api/personalization/similar/{user_id}     similar users by embedding
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models.personalization import (
    PreferencesUpdateRequest,
    ProfileBuildResponse,
    ProfileUpdateRequest,
    SimilarUserMatch,
    UnifiedUserProfile,
    PersonalizedRecommendationsResponse,
)
from app.personalization.embeddings import UserEmbeddingService
from app.personalization.preferences import LearningPreferenceTracker
from app.personalization.profile_engine import UserProfileEngine
from app.personalization.recommender import PersonalizedRecommender
from app.personalization.store import get_profile_store
from app.services.user_service import UserService

router = APIRouter(prefix="/personalization", tags=["personalization"])


async def _default_user_id(db: AsyncSession | None) -> str:
    user = await UserService.get_demo_user(db)
    return user.id


@router.get("/profile/{user_id}", response_model=UnifiedUserProfile)
async def get_profile(
    user_id: str,
    refresh: bool = Query(False),
    db: AsyncSession | None = Depends(get_optional_db),
) -> UnifiedUserProfile:
    return await UserProfileEngine.get_or_build(user_id, db, refresh=refresh)


@router.post("/profile/build", response_model=ProfileBuildResponse)
async def build_profile(
    user_id: str | None = Query(None),
    db: AsyncSession | None = Depends(get_optional_db),
) -> ProfileBuildResponse:
    uid = user_id or await _default_user_id(db)
    profile, used_ml = await UserProfileEngine.refresh_embedding(uid, db)
    recs = PersonalizedRecommender.recommend(profile)
    return ProfileBuildResponse(
        profile=profile,
        recommendations=recs,
        embedding_updated=used_ml,
    )


@router.patch("/profile/{user_id}", response_model=UnifiedUserProfile)
async def update_profile(
    user_id: str,
    body: ProfileUpdateRequest,
    db: AsyncSession | None = Depends(get_optional_db),
) -> UnifiedUserProfile:
    profile = await UserProfileEngine.update(user_id, body, db)
    UserEmbeddingService.embed_profile(profile)
    return profile


@router.patch("/preferences/{user_id}", response_model=UnifiedUserProfile)
async def update_preferences(
    user_id: str,
    body: PreferencesUpdateRequest,
    db: AsyncSession | None = Depends(get_optional_db),
) -> UnifiedUserProfile:
    profile = await UserProfileEngine.get_or_build(user_id, db)
    inferred = None
    if body.style_scores:
        inferred = body.style_scores
    prefs = LearningPreferenceTracker.merge_preferences(
        profile.learning_preferences,
        inferred=inferred,
        explicit_style=body.primary_style,
    )
    if body.preferred_session_minutes is not None:
        prefs.preferred_session_minutes = body.preferred_session_minutes
    if body.preferred_study_time is not None:
        prefs.preferred_study_time = body.preferred_study_time
    if body.content_formats is not None:
        prefs.content_formats = body.content_formats

    profile.learning_preferences = prefs
    from app.personalization.profile_engine import _build_summary, _now

    profile.profile_summary = _build_summary(profile)
    profile.updated_at = _now()
    get_profile_store().save(profile)
    UserEmbeddingService.embed_profile(profile)
    return profile


@router.get("/recommendations/{user_id}", response_model=PersonalizedRecommendationsResponse)
async def get_personalized_recommendations(
    user_id: str,
    db: AsyncSession | None = Depends(get_optional_db),
) -> PersonalizedRecommendationsResponse:
    profile = await UserProfileEngine.get_or_build(user_id, db)
    return PersonalizedRecommender.recommend(profile)


@router.get("/recommendations", response_model=PersonalizedRecommendationsResponse)
async def get_demo_recommendations(
    db: AsyncSession | None = Depends(get_optional_db),
) -> PersonalizedRecommendationsResponse:
    uid = await _default_user_id(db)
    profile = await UserProfileEngine.get_or_build(uid, db)
    return PersonalizedRecommender.recommend(profile)


@router.get("/similar/{user_id}", response_model=list[SimilarUserMatch])
async def similar_users(user_id: str) -> list[SimilarUserMatch]:
    matches = UserEmbeddingService.find_similar(user_id)
    if not matches:
        raise HTTPException(status_code=404, detail="No embedding found for user — call POST /profile/build first")

    out: list[SimilarUserMatch] = []
    store = get_profile_store()
    target = store.get(user_id)
    target_weak = set(target.weak_subjects if target else [])

    for other_id, sim in matches:
        other = store.get(other_id)
        shared = list(target_weak & set(other.weak_subjects if other else []))
        out.append(
            SimilarUserMatch(
                user_id=other_id,
                similarity=round(sim, 3),
                shared_weak_subjects=shared,
                learning_style=other.learning_preferences.primary_style if other else "unknown",
            )
        )
    return out
