"""
Statistics API routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models import PostHistory, Reply, Opportunity, TelegramGroup, Notification
from app.schemas import StatisticsResponse
from app.api.auth import get_current_user
from app.models import User
from datetime import datetime, timedelta

router = APIRouter()

@router.get("", response_model=StatisticsResponse)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's posting statistics"""
    
    # Count groups
    total_groups = db.query(TelegramGroup).join(
        User.groups
    ).filter(User.id == current_user.id).count()
    
    active_groups = db.query(TelegramGroup).join(
        User.groups
    ).filter(
        (User.id == current_user.id) &
        (TelegramGroup.member_count > 0)
    ).count()
    
    # Count posts
    total_posts = db.query(PostHistory).filter(
        (PostHistory.user_id == current_user.id) &
        (PostHistory.status == "success")
    ).count()
    
    # Posts this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    posts_this_week = db.query(PostHistory).filter(
        (PostHistory.user_id == current_user.id) &
        (PostHistory.status == "success") &
        (PostHistory.created_at >= week_ago)
    ).count()
    
    # Skipped and failed
    skipped_posts = db.query(PostHistory).filter(
        (PostHistory.user_id == current_user.id) &
        (PostHistory.status == "skipped")
    ).count()
    
    failed_posts = db.query(PostHistory).filter(
        (PostHistory.user_id == current_user.id) &
        (PostHistory.status == "failed")
    ).count()
    
    # Replies
    total_replies = db.query(Reply).filter(
        Reply.user_id == current_user.id
    ).count()
    
    unread_replies = db.query(Notification).filter(
        (Notification.user_id == current_user.id) &
        (Notification.is_read == False)
    ).count()
    
    # Opportunities
    opportunities_identified = db.query(Opportunity).filter(
        Opportunity.user_id == current_user.id
    ).count()
    
    # Last post
    last_post = db.query(PostHistory).filter(
        (PostHistory.user_id == current_user.id) &
        (PostHistory.status == "success")
    ).order_by(PostHistory.created_at.desc()).first()
    
    # Next scheduled post (placeholder)
    next_post_at = None
    
    return {
        "total_groups": total_groups,
        "active_groups": active_groups,
        "total_posts": total_posts,
        "posts_this_week": posts_this_week,
        "skipped_posts": skipped_posts,
        "failed_posts": failed_posts,
        "total_replies": total_replies,
        "unread_replies": unread_replies,
        "opportunities_identified": opportunities_identified,
        "last_post_at": last_post.created_at if last_post else None,
        "next_scheduled_post": next_post_at
    }
