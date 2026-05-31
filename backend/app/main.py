from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth.rate_limit import limiter
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routes import (
    agents,
    ai_platform,
    auth,
    coach,
    conversations,
    dashboard,
    documents,
    health,
    interview,
    memory,
    personalization,
    recommendations,
    study_planner,
    study_agent,
    study_tools,
    career_agent,
    resume,
    learning_planner,
    learning_analytics,
    mlops,
    monitoring,
    reports,
    tip,
    user,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        from app.database.init_db import create_tables

        await create_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI Personalized Learning & Interview Coach API",
    version="0.9.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
register_exception_handlers(app)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

app.include_router(health.router, prefix=API_PREFIX, tags=["health"])
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(user.router, prefix=API_PREFIX, tags=["user"])
# Week 3 Day 7 — unified AI platform (canonical routes)
app.include_router(ai_platform.router, prefix=API_PREFIX)
app.include_router(ai_platform.router)  # POST /predict, GET /insights at root too
app.include_router(recommendations.router, prefix=API_PREFIX, tags=["recommendations"])
app.include_router(study_planner.router, prefix=API_PREFIX, tags=["study-planner"])
app.include_router(dashboard.router, prefix=API_PREFIX, tags=["dashboard"])
app.include_router(coach.router, prefix=API_PREFIX)
app.include_router(personalization.router, prefix=API_PREFIX)
app.include_router(memory.router, prefix=API_PREFIX)
app.include_router(learning_analytics.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(mlops.router, prefix=API_PREFIX)
app.include_router(monitoring.router, prefix=API_PREFIX)
app.include_router(tip.router, prefix=API_PREFIX, tags=["ai"])
# Week 4 Day 2 — PDF processing / document upload
app.include_router(documents.router, prefix=API_PREFIX)
# Week 4 Day 5 — smart learning features (summarize, quiz, flashcards, etc.)
app.include_router(study_tools.router, prefix=API_PREFIX)
# Week 4 Day 6 — conversation memory (chat sessions)
app.include_router(conversations.router, prefix=API_PREFIX)
# Week 5 Day 1 — AI Interview Coach
app.include_router(interview.router, prefix=API_PREFIX)
# Week 6 Day 1 — AI Agent Router (Study / Interview / Career / Resume)
app.include_router(agents.router, prefix=API_PREFIX)
# Week 6 Day 2 — Study Agent tutor API
app.include_router(study_agent.router, prefix=API_PREFIX)
# Week 6 Day 3 — Career Agent API
app.include_router(career_agent.router, prefix=API_PREFIX)
# Week 6 Day 4 — Resume Analyzer
app.include_router(resume.router, prefix=API_PREFIX)
# Week 6 Day 5 — Personalized Learning Planner
app.include_router(learning_planner.router, prefix=API_PREFIX)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.9.0",
        "docs": "/docs",
        "week3_ai_platform": {
            "predict": "POST /predict",
            "recommend": "POST /recommend",
            "analytics": "GET /analytics",
            "insights": "GET /insights",
            "status": "GET /api/ai/status",
        },
        "endpoints": {
            "health": f"{API_PREFIX}/health",
            "auth_register": f"{API_PREFIX}/auth/register",
            "auth_login": f"{API_PREFIX}/auth/login",
            "auth_refresh": f"{API_PREFIX}/auth/refresh",
            "auth_me": f"{API_PREFIX}/auth/me",
            "predict": f"{API_PREFIX}/predict",
            "recommend": f"{API_PREFIX}/recommend",
            "analytics": f"{API_PREFIX}/analytics",
            "insights": f"{API_PREFIX}/insights",
            "predict_explain": f"{API_PREFIX}/predict/explain",
            "dashboard": f"{API_PREFIX}/dashboard",
            "coach_overview": f"{API_PREFIX}/coach/overview",
            "coach_weekly_report": f"{API_PREFIX}/coach/weekly-report",
            "personalization_profile": f"{API_PREFIX}/personalization/profile/{{user_id}}",
            "personalization_recommendations": f"{API_PREFIX}/personalization/recommendations",
            "memory_progress": f"{API_PREFIX}/memory/demo/progress",
            "memory_context": f"{API_PREFIX}/memory/{{user_id}}/context",
            "learning_analytics": f"{API_PREFIX}/learning-analytics/demo",
            "reports_weekly": f"{API_PREFIX}/reports/demo/weekly",
            "reports_monthly": f"{API_PREFIX}/reports/demo/monthly",
            "mlops_status": f"{API_PREFIX}/mlops/status",
            "mlops_models": f"{API_PREFIX}/mlops/models",
            "mlops_experiments": f"{API_PREFIX}/mlops/experiments",
            "mlops_compare": f"{API_PREFIX}/mlops/experiments/compare",
            "mlops_promote": f"{API_PREFIX}/mlops/models/promote",
            "monitoring_feedback": f"{API_PREFIX}/monitoring/feedback",
            "monitoring_dashboard": f"{API_PREFIX}/monitoring/demo",
            "monitoring_satisfaction": f"{API_PREFIX}/monitoring/satisfaction/demo-user-001",
            "study_planner": f"{API_PREFIX}/study-planner",
            "daily_tip": f"{API_PREFIX}/daily-tip",
            "documents_upload": f"{API_PREFIX}/documents/upload",
            "documents": f"{API_PREFIX}/documents",
            "documents_search": f"{API_PREFIX}/documents/search",
            "documents_chat": f"{API_PREFIX}/documents/chat",
            "study_tools": f"{API_PREFIX}/study/(summarize|quiz|flashcards|explain|revision)",
            "chat_sessions": f"{API_PREFIX}/chat/sessions",
            "interview": f"{API_PREFIX}/interview/start",
            "interview_transcribe": f"{API_PREFIX}/interview/transcribe",
            "interview_emotion": f"{API_PREFIX}/interview/emotion/analyze",
            "agents_types": f"{API_PREFIX}/agents/types",
            "agents_chat": f"{API_PREFIX}/agents/chat",
            "agents_session": f"{API_PREFIX}/agents/session/{{session_id}}",
            "study_agent_plan": f"{API_PREFIX}/agents/study/plan",
            "study_agent_daily": f"{API_PREFIX}/agents/study/daily",
            "study_agent_goals": f"{API_PREFIX}/agents/study/goals/{{session_id}}",
            "career_recommend": f"{API_PREFIX}/agents/career/recommend",
            "career_roadmap": f"{API_PREFIX}/agents/career/roadmap",
            "career_trends": f"{API_PREFIX}/agents/career/trends",
            "resume_upload": f"{API_PREFIX}/resume/upload",
            "resume_analyze": f"{API_PREFIX}/resume/analyze",
            "resume_analysis": f"{API_PREFIX}/resume/analysis/{{analysis_id}}",
            "learning_planner_roadmap": f"{API_PREFIX}/learning-planner/roadmap",
            "learning_planner_plans": f"{API_PREFIX}/learning-planner/plans",
        },
    }
