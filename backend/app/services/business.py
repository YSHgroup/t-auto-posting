"""
Business logic services
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    TelegramGroup, GroupAnalysis, PostHistory, Reply, Post, 
    User, GroupFeed, Notification
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class GroupService:
    """Group management service"""
    
    @staticmethod
    def should_skip_posting(db: Session, user_id: int, group_id: int) -> tuple[bool, str]:
        """
        Check if posting to this group should be skipped.
        Returns (should_skip, reason)
        """
        # Get last post to this group
        last_post = db.query(PostHistory).filter(
            (PostHistory.user_id == user_id) &
            (PostHistory.group_id == group_id) &
            (PostHistory.status == "success")
        ).order_by(PostHistory.created_at.desc()).first()
        
        if not last_post:
            # Never posted before
            return False, ""
        
        # Get user's minimum message threshold
        from app.models import SchedulerSettings
        settings_record = db.query(SchedulerSettings).filter(
            SchedulerSettings.user_id == user_id
        ).first()
        
        min_messages = settings_record.min_messages_between_posts if settings_record else 20
        
        # TODO: Get message count between last post and now
        # This would require fetching from Telegram
        # For now, use a simple check based on time
        
        time_since_last = datetime.utcnow() - last_post.created_at
        if time_since_last < timedelta(seconds=60):
            return True, f"Posted to group {time_since_last.total_seconds():.0f}s ago (min 60s required)"
        
        return False, ""
    
    @staticmethod
    def get_posting_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """Get posting statistics for a user"""
        today = datetime.utcnow().date()
        
        total_posts = db.query(PostHistory).filter(
            (PostHistory.user_id == user_id) &
            (PostHistory.status == "success")
        ).count()
        
        posts_today = db.query(PostHistory).filter(
            (PostHistory.user_id == user_id) &
            (PostHistory.status == "success") &
            (PostHistory.created_at >= datetime.combine(today, datetime.min.time()))
        ).count()
        
        skipped_posts = db.query(PostHistory).filter(
            (PostHistory.user_id == user_id) &
            (PostHistory.status == "skipped")
        ).count()
        
        return {
            "total_posts": total_posts,
            "posts_today": posts_today,
            "skipped_posts": skipped_posts
        }


class PostingService:
    """Posting operation service"""
    
    @staticmethod
    def create_post_history(
        db: Session,
        user_id: int,
        group_id: int,
        post_id: Optional[int],
        status: str,
        reason: Optional[str] = None,
        telegram_message_id: Optional[str] = None,
        skip_reason: Optional[str] = None,
        posted_at: Optional[datetime] = None,
    ) -> PostHistory:
        """Record a posting attempt"""
        history = PostHistory(
            user_id=user_id,
            group_id=group_id,
            post_id=post_id,
            status=status,
            reason=reason or skip_reason,
            telegram_message_id=telegram_message_id,
            posted_at=posted_at or (datetime.utcnow() if status == "success" else None),
            created_at=datetime.utcnow()
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return history
    
    @staticmethod
    def delete_previous_post(db: Session, user_id: int, group_id: int) -> bool:
        """Delete user's previous post in a group"""
        # TODO: Implement message deletion via Telegram
        return True
    
    @staticmethod
    def record_rate_limit_error(db: Session, user_id: int, wait_seconds: int, group_id: Optional[int] = None):
        """Record rate limit error and backoff"""
        logger.warning(f"Rate limited for user {user_id}: wait {wait_seconds}s")
        return {"user_id": user_id, "group_id": group_id, "wait_seconds": wait_seconds}


class ReplyService:
    """Reply monitoring service"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        reply_id: int,
        is_read: bool = False
    ) -> Notification:
        """Create notification for a reply"""
        notification = Notification(
            user_id=user_id,
            reply_id=reply_id,
            is_read=is_read,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get count of unread notifications"""
        return db.query(Notification).filter(
            (Notification.user_id == user_id) &
            (Notification.is_read == False)
        ).count()


class SchedulerService:
    """Scheduler service"""
    
    @staticmethod
    def is_in_active_window(
        db: Session,
        user_id: int,
        current_time: Optional[datetime] = None
    ) -> bool:
        """Check if current time is within user's active posting window"""
        from app.models import SchedulerSettings
        import pytz
        
        settings = db.query(SchedulerSettings).filter(
            SchedulerSettings.user_id == user_id
        ).first()
        
        if not settings or settings.posting_mode != "automatic":
            return False

        if current_time is None:
            current_time = datetime.utcnow()
        if settings.timezone and settings.timezone != "UTC":
            try:
                current_time = pytz.utc.localize(current_time).astimezone(pytz.timezone(settings.timezone))
            except pytz.UnknownTimeZoneError:
                logger.warning("Unknown scheduler timezone %s; using UTC", settings.timezone)
        
        # Parse active times
        start_hour, start_min = map(int, settings.active_start_time.split(":"))
        end_hour, end_min = map(int, settings.active_end_time.split(":"))
        
        # Parse active days (1=Monday, 7=Sunday)
        active_days = [int(d) for d in settings.active_days.split(",")]
        current_day = current_time.weekday() + 1  # Python weekday: 0=Monday, so +1
        
        # Check day
        if current_day not in active_days:
            return False
        
        # Check time
        current_hour, current_min = current_time.hour, current_time.minute
        current_total_min = current_hour * 60 + current_min
        start_total_min = start_hour * 60 + start_min
        end_total_min = end_hour * 60 + end_min
        
        if start_total_min <= end_total_min:
            return start_total_min <= current_total_min <= end_total_min
        return current_total_min >= start_total_min or current_total_min <= end_total_min
    
    @staticmethod
    def get_next_group_in_feed(
        db: Session,
        user_id: int,
        last_group_id: Optional[int] = None
    ) -> Optional[int]:
        """Get next group to post to in feed order"""
        query = db.query(GroupFeed).filter(
            (GroupFeed.user_id == user_id) &
            (GroupFeed.is_enabled == True)
        ).order_by(GroupFeed.position)
        
        if last_group_id:
            current = query.filter(GroupFeed.group_id == last_group_id).first()
            if current:
                query = query.filter(GroupFeed.position > current.position)
        
        feed_item = query.first()
        return feed_item.group_id if feed_item else None
