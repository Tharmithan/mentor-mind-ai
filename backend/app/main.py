from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import (
    agents,
    ai_platform,
    conversations,
    dashboard,
    documents,
    health,
    interview,
    recommendations,
    study_planner,
    study_agent,
    study_tools,
    tip,
    user,
)

app = FastAPI(
    title=settings.app_name,
    description="AI Personalized Learning & Interview Coach API",
    version="0.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

app.include_router(health.router, prefix=API_PREFIX, tags=["health"])
app.include_router(user.router, prefix=API_PREFIX, tags=["user"])
# Week 3 Day 7 — unified AI platform (canonical routes)
app.include_router(ai_platform.router, prefix=API_PREFIX)
app.include_router(ai_platform.router)  # POST /predict, GET /insights at root too
app.include_router(recommendations.router, prefix=API_PREFIX, tags=["recommendations"])
app.include_router(study_planner.router, prefix=API_PREFIX, tags=["study-planner"])
app.include_router(dashboard.router, prefix=API_PREFIX, tags=["dashboard"])
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


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.6.0",
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
            "predict": f"{API_PREFIX}/predict",
            "recommend": f"{API_PREFIX}/recommend",
            "analytics": f"{API_PREFIX}/analytics",
            "insights": f"{API_PREFIX}/insights",
            "predict_explain": f"{API_PREFIX}/predict/explain",
            "dashboard": f"{API_PREFIX}/dashboard",
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
        },
    }
