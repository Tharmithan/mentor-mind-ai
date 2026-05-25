from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import User
from app.models.dashboard import ChartPoint, DashboardResponse, WeakSubject
from app.models.recommendation import RecommendationItem

_WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_DEFAULT_HOURS = [2.5, 4.0, 3.0, 5.0, 3.5, 6.0, 4.5]
_DEFAULT_TREND = [68, 72, 75, 78, 82]


class DashboardService:
    @staticmethod
    async def get_dashboard(session: AsyncSession | None) -> DashboardResponse:
        if session is None:
            return DashboardService._mock_dashboard()

        result = await session.execute(
            select(User)
            .options(
                selectinload(User.performance_data),
                selectinload(User.recommendations),
            )
            .limit(1)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return DashboardService._mock_dashboard()

        return DashboardService._build_from_user(user)

    @staticmethod
    def _build_from_user(user: User) -> DashboardResponse:
        perf = sorted(user.performance_data, key=lambda p: float(p.score))
        performance_score = (
            round(sum(float(p.score) for p in perf) / len(perf), 1) if perf else 82.0
        )

        weak = [
            WeakSubject(subject=p.subject, score=float(p.score))
            for p in perf
            if float(p.score) < 70
        ]
        if not weak and perf:
            weakest = min(perf, key=lambda p: float(p.score))
            weak = [WeakSubject(subject=weakest.subject, score=float(weakest.score))]

        subject_distribution = [
            ChartPoint(label=p.subject, value=float(p.score)) for p in perf
        ] or [
            ChartPoint(label="Mathematics", value=91),
            ChartPoint(label="Programming", value=78),
            ChartPoint(label="Data Structures", value=62),
        ]

        total_hours = sum(float(p.study_hours or 0) for p in perf) or 28.5
        scale = total_hours / sum(_DEFAULT_HOURS) if sum(_DEFAULT_HOURS) else 1
        study_hours_by_day = [
            ChartPoint(label=day, value=round(h * scale, 1))
            for day, h in zip(_WEEK_DAYS, _DEFAULT_HOURS)
        ]

        trend_base = _DEFAULT_TREND[:-1] + [performance_score]
        performance_trend = [
            ChartPoint(label=f"W{i + 1}", value=float(v))
            for i, v in enumerate(trend_base)
        ]

        recs = sorted(user.recommendations, key=lambda r: r.created_at, reverse=True)
        recommendations = [
            RecommendationItem(
                id=str(r.id),
                title=r.title,
                description=r.description,
                topic=r.topic,
                priority=r.priority,
                is_completed=r.is_completed,
            )
            for r in recs
        ]

        return DashboardResponse(
            performance_score=performance_score,
            study_hours_week=round(total_hours, 1),
            weak_subjects=weak,
            ai_suggestions_count=len([r for r in recs if not r.is_completed]),
            study_hours_by_day=study_hours_by_day,
            performance_trend=performance_trend,
            subject_distribution=subject_distribution,
            recommendations=recommendations,
        )

    @staticmethod
    def _mock_dashboard() -> DashboardResponse:
        from app.services.recommendation_service import RecommendationService

        mock_recs = RecommendationService._engine_recommendations().recommendations
        pending = len([r for r in mock_recs if not r.is_completed])

        return DashboardResponse(
            performance_score=82.0,
            study_hours_week=28.5,
            weak_subjects=[
                WeakSubject(subject="Data Structures", score=62),
            ],
            ai_suggestions_count=pending,
            study_hours_by_day=[
                ChartPoint(label=d, value=h)
                for d, h in zip(_WEEK_DAYS, _DEFAULT_HOURS)
            ],
            performance_trend=[
                ChartPoint(label=f"W{i + 1}", value=float(v))
                for i, v in enumerate(_DEFAULT_TREND)
            ],
            subject_distribution=[
                ChartPoint(label="Mathematics", value=91),
                ChartPoint(label="Programming", value=78),
                ChartPoint(label="Data Structures", value=62),
            ],
            recommendations=mock_recs,
        )
