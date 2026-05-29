from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import (
    ai_platform,
    dashboard,
    documents,
    health,
    recommendations,
    study_planner,
    tip,
    user,
)

app = FastAPI(
    title=settings.app_name,
    description="AI Personalized Learning & Interview Coach API",
    version="0.4.0",
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


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.4.0",
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
        },
    }
