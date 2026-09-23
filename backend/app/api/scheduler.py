"""
Scheduler API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import SchedulerSettings
from app.schemas import SchedulerConfig, SchedulerStatus
from app.api.auth import get_current_user
from app.models import User
from datetime import datetime

router = APIRouter()

@router.get("/config", response_model=SchedulerConfig)
async def get_scheduler_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's scheduler configuration"""
    settings = db.query(SchedulerSettings).filter(
        SchedulerSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings
        settings = SchedulerSettings(
            user_id=current_user.id,
            posting_mode="manual",
            active_start_time="09:00",
            active_end_time="20:00",
            active_days="1,2,3,4,5",
            timezone="UTC"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings

@router.put("/config", response_model=SchedulerConfig)
async def update_scheduler_config(
    request: SchedulerConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update scheduler configuration"""
    settings = db.query(SchedulerSettings).filter(
        SchedulerSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = SchedulerSettings(user_id=current_user.id)
    
    settings.posting_mode = request.posting_mode
    settings.active_start_time = request.active_start_time
    settings.active_end_time = request.active_end_time
    settings.active_days = request.active_days
    settings.timezone = request.timezone
    settings.min_messages_between_posts = request.min_messages_between_posts
    settings.max_posts_per_hour = request.max_posts_per_hour
    settings.max_posts_per_day = request.max_posts_per_day
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    return settings

@router.post("/start")
async def start_scheduler(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start automatic posting"""
    settings = db.query(SchedulerSettings).filter(
        SchedulerSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Scheduler settings not found")
    
    settings.posting_mode = "automatic"
    db.commit()
    
    # TODO: Start Celery beat scheduler task
    return {"status": "scheduler_started"}

@router.post("/pause")
async def pause_scheduler(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause automatic posting"""
    settings = db.query(SchedulerSettings).filter(
        SchedulerSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Scheduler settings not found")
    
    settings.posting_mode = "manual"
    db.commit()
    
    # TODO: Stop Celery beat scheduler task
    return {"status": "scheduler_paused"}

@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scheduler status"""
    settings = db.query(SchedulerSettings).filter(
        SchedulerSettings.user_id == current_user.id
    ).first()
    
    # TODO: Fetch actual stats from database
    return {
        "is_running": settings.posting_mode == "automatic" if settings else False,
        "posting_mode": settings.posting_mode if settings else "manual",
        "last_post_at": None,
        "next_post_at": None,
        "posts_today": 0,
        "posts_this_hour": 0
    }
