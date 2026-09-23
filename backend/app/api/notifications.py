"""
Notifications API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Notification, Reply
from app.schemas import NotificationResponse
from typing import List
from app.api.auth import get_current_user
from app.models import User
from datetime import datetime

router = APIRouter()

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50
):
    """Get user's notifications"""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notifications

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    unread_count = db.query(Notification).filter(
        (Notification.user_id == current_user.id) &
        (Notification.is_read == False)
    ).count()
    
    return {"unread_count": unread_count}

@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        (Notification.id == notification_id) &
        (Notification.user_id == current_user.id)
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"status": "marked_as_read"}

@router.put("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        (Notification.user_id == current_user.id) &
        (Notification.is_read == False)
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    
    db.commit()
    
    return {"status": "all_marked_as_read"}
