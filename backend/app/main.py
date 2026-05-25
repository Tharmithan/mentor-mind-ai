from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import dashboard, health, predict, recommendations, tip, user

app = FastAPI(
    title=settings.app_name,
    description="AI Personalized Learning & Interview Coach API",
    version="0.2.0",
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
app.include_router(predict.router, prefix=API_PREFIX, tags=["predict"])
app.include_router(predict.router, tags=["predict"])  # POST /predict (Day 7)
app.include_router(recommendations.router, prefix=API_PREFIX, tags=["recommendations"])
app.include_router(dashboard.router, prefix=API_PREFIX, tags=["dashboard"])
app.include_router(tip.router, prefix=API_PREFIX, tags=["ai"])


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.3.0",
        "docs": "/docs",
        "ml_api": f"{API_PREFIX}/predict",
        "endpoints": {
            "health": f"{API_PREFIX}/health",
            "user": f"{API_PREFIX}/user",
            "predict": f"{API_PREFIX}/predict",
            "recommendations": f"{API_PREFIX}/recommendations",
            "dashboard": f"{API_PREFIX}/dashboard",
            "daily_tip": f"{API_PREFIX}/daily-tip",
        },
    }
