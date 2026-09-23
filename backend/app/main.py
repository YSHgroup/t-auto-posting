"""
Backend configuration and initialization
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, groups, feed, posts, scheduler, notifications, opportunities, statistics
from app.api import telegram_auth

# Create tables on startup
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Telegram Intelligence Bot API...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Telegram Intelligence & Posting Bot",
    description="AI-powered Telegram group analysis and automatic posting system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(telegram_auth.router, prefix="/api", tags=["Telegram"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(feed.router, prefix="/api/feed", tags=["Feed"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["Scheduler"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["Opportunities"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["Statistics"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

@app.get("/docs-custom")
async def docs():
    """Custom documentation page"""
    return {
        "message": "API Documentation available at /docs",
        "swagger_ui": "/docs",
        "openapi": "/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
