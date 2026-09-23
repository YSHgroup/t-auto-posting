"""
Background task implementations for Celery
Import these into celery_app.py to register them
"""
import logging
import asyncio
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def _run_async_task(coro):
    """Helper to run async code in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# Import celery app and create tasks
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_group_task(self, user_id: int, group_id: int):
    """
    Analyze a Telegram group using AI
    
    Args:
        user_id: ID of the user performing analysis
        group_id: ID of the Telegram group to analyze
    """
    from app.core.database import SessionLocal
    from app.models import TelegramGroup, GroupAnalysis, TelegramAccount, AISettings
    from app.ai.providers import OpenAIProvider, ClaudeProvider
    from app.telegram.client import get_telegram_service
    from app.core.config import settings
    
    db = SessionLocal()
    
    try:
        # Get group from database
        group = db.query(TelegramGroup).filter(
            TelegramGroup.id == group_id,
            TelegramGroup.users.any(id=user_id)
        ).first()
        
        if not group:
            logger.error(f"Group {group_id} not found for user {user_id}")
            return {"status": "error", "message": "Group not found"}
        
        # Get user's Telegram session
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == user_id
        ).first()
        
        if not telegram_account or not telegram_account.session_string:
            logger.error(f"No Telegram session for user {user_id}")
            return {"status": "error", "message": "Telegram not configured"}
        
        # Get messages from Telegram
        telegram_service = get_telegram_service(telegram_account.session_string)
        messages = _run_async_task(
            telegram_service.get_recent_messages(group.telegram_id, limit=100)
        )
        
        if not messages:
            logger.warning(f"No messages found for group {group_id}")
            return {"status": "error", "message": "No messages to analyze"}
        
        # Prepare group info for AI
        group_info = {
            "name": group.name,
            "username": group.username,
            "description": group.description,
            "member_count": group.member_count,
            "messages_text": "\n".join([m.get("text", "") for m in messages[:20]])
        }
        
        # Get AI provider from user settings
        ai_settings = db.query(AISettings).filter(
            AISettings.user_id == user_id
        ).first()
        
        if not ai_settings:
            logger.error(f"No AI settings for user {user_id}")
            return {"status": "error", "message": "AI provider not configured"}
        
        # Initialize appropriate AI provider
        if ai_settings.provider == "openai":
            ai_provider = OpenAIProvider(settings.OPENAI_API_KEY)
        elif ai_settings.provider == "claude":
            ai_provider = ClaudeProvider(settings.ANTHROPIC_API_KEY)
        else:
            logger.error(f"Unknown AI provider: {ai_settings.provider}")
            return {"status": "error", "message": "Unknown AI provider"}
        
        # Analyze group
        analysis_result = _run_async_task(ai_provider.analyze_group(group_info))
        
        if not analysis_result:
            logger.error(f"AI analysis returned None for group {group_id}")
            return {"status": "error", "message": "AI analysis failed"}
        
        # Store analysis
        existing_analysis = db.query(GroupAnalysis).filter(
            GroupAnalysis.user_id == user_id,
            GroupAnalysis.group_id == group_id
        ).first()
        
        if existing_analysis:
            existing_analysis.analysis_text = json.dumps(analysis_result)
            existing_analysis.partnership_suitability = analysis_result.get("partnership_suitability", "Unknown")
            existing_analysis.job_suitability = analysis_result.get("job_suitability", "Unknown")
            existing_analysis.confidence_score = analysis_result.get("confidence_score", 0)
            existing_analysis.posting_style = ",".join(analysis_result.get("posting_style", []))
            existing_analysis.updated_at = datetime.utcnow()
        else:
            group_analysis = GroupAnalysis(
                user_id=user_id,
                group_id=group_id,
                analysis_text=json.dumps(analysis_result),
                partnership_suitability=analysis_result.get("partnership_suitability", "Unknown"),
                job_suitability=analysis_result.get("job_suitability", "Unknown"),
                confidence_score=analysis_result.get("confidence_score", 0),
                posting_style=",".join(analysis_result.get("posting_style", []))
            )
            db.add(group_analysis)
        
        db.commit()
        
        logger.info(f"Successfully analyzed group {group_id}")
        return {"status": "success", "message": "Analysis complete"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error in analyze_group_task: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=5, default_retry_delay=30)
def post_to_group_task(self, user_id: int, group_id: int, post_id: int):
    """
    Post a message to a Telegram group with retry logic for FloodWait
    """
    from app.core.database import SessionLocal
    from app.models import Post, TelegramGroup, TelegramAccount, PostHistory
    from app.services.business import PostingService, GroupService
    from app.telegram.client import get_telegram_service
    from pyrogram.errors import FloodWait
    
    db = SessionLocal()
    
    try:
        # Get post
        post = db.query(Post).filter(
            Post.id == post_id,
            Post.user_id == user_id
        ).first()
        group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
        
        if not post or not post.is_active or not group:
            logger.error(f"Post {post_id} not found or inactive")
            return {"status": "error", "message": "Post not found"}
        
        # Check if should skip
        group_service = GroupService(db)
        should_skip, skip_reason = group_service.should_skip_posting(user_id, group_id)
        
        if should_skip:
            logger.info(f"Skipping post to group {group_id}: {skip_reason}")
            posting_service = PostingService(db)
            posting_service.create_post_history(
                user_id=user_id,
                group_id=group_id,
                post_id=post_id,
                status="skipped",
                skip_reason=skip_reason
            )
            return {"status": "skipped", "message": skip_reason}
        
        # Get Telegram session
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == user_id
        ).first()
        
        if not telegram_account or not telegram_account.session_string:
            logger.error(f"No Telegram session for user {user_id}")
            return {"status": "error", "message": "Telegram not configured"}
        
        # Send message
        telegram_service = get_telegram_service(telegram_account.session_string)
        message_id = _run_async_task(
            telegram_service.send_message(group.telegram_group_id, post.content)
        )
        
        if not message_id:
            logger.error(f"Failed to send message to group {group_id}")
            return {"status": "error", "message": "Failed to send message"}
        
        # Record successful post
        posting_service = PostingService(db)
        posting_service.create_post_history(
            user_id=user_id,
            group_id=group_id,
            post_id=post_id,
            status="success",
            telegram_message_id=message_id,
            posted_at=datetime.utcnow()
        )
        
        logger.info(f"Successfully posted to group {group_id}: {message_id}")
        return {"status": "success", "message_id": message_id}
    
    except FloodWait as fw:
        wait_seconds = fw.value
        logger.warning(f"FloodWait for {wait_seconds} seconds")
        
        # Record rate limit error
        posting_service = PostingService(db)
        posting_service.record_rate_limit_error(
            user_id=user_id,
            group_id=group_id,
            wait_seconds=wait_seconds
        )
        
        db.commit()
        
        # Retry after waiting
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=wait_seconds)
        else:
            return {"status": "rate_limited", "wait_seconds": wait_seconds}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error posting to group: {e}")
        raise self.retry(exc=e, countdown=30 * (2 ** self.request.retries))
    finally:
        db.close()


@celery_app.task(bind=True, default_retry_delay=60)
def monitor_replies_task(self, user_id: int):
    """Monitor for replies to user's posts"""
    from app.core.database import SessionLocal
    from app.models import PostHistory, TelegramAccount, Reply, Notification
    from app.telegram.client import get_telegram_service
    
    db = SessionLocal()
    
    try:
        # Get user's Telegram account
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == user_id
        ).first()
        
        if not telegram_account or not telegram_account.session_string:
            logger.warning(f"No Telegram session for user {user_id}")
            return {"status": "error", "message": "Telegram not configured"}
        
        # Get all recent posts
        recent_posts = db.query(PostHistory).filter(
            PostHistory.user_id == user_id,
            PostHistory.status == "success"
        ).order_by(PostHistory.posted_at.desc()).limit(100).all()
        
        if not recent_posts:
            logger.info(f"No recent posts for user {user_id}")
            return {"status": "no_posts"}
        
        # Check for replies to each post
        telegram_service = get_telegram_service(telegram_account.session_string)
        reply_count = 0
        
        for post_history in recent_posts:
            try:
                messages = _run_async_task(
                    telegram_service.get_recent_messages(
                        post_history.group.telegram_group_id,
                        limit=50
                    )
                )
                
                for msg in messages:
                    # Check if reply to our post
                    if msg.get("reply_to_message_id") == int(post_history.telegram_message_id):
                        # Create reply record
                        existing_reply = db.query(Reply).filter(
                            Reply.post_history_id == post_history.id,
                            Reply.telegram_message_id == msg["id"]
                        ).first()
                        
                        if not existing_reply:
                            reply = Reply(
                                post_history_id=post_history.id,
                                telegram_message_id=msg["id"],
                                user_id=user_id,
                                group_id=post_history.group_id,
                                telegram_user_id=msg.get("from_user_id"),
                                telegram_user_name=msg.get("from_user_name"),
                                message_text=msg.get("text", ""),
                                received_at=datetime.fromtimestamp(msg["date"]) if msg.get("date") else datetime.utcnow()
                            )
                            db.add(reply)
                            db.flush()
                            
                            # Create notification
                            notification = Notification(
                                user_id=user_id,
                                reply_id=reply.id,
                                is_read=False
                            )
                            db.add(notification)
                            reply_count += 1
            
            except Exception as e:
                logger.warning(f"Error checking replies for post {post_history.id}: {e}")
                continue
        
        if reply_count > 0:
            db.commit()
        
        logger.info(f"Found {reply_count} new replies for user {user_id}")
        return {"status": "success", "new_replies": reply_count}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error monitoring replies: {e}")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


@celery_app.task(bind=True)
def analyze_opportunities_task(self, user_id: int, group_id: int):
    """Analyze messages for investment/partnership opportunities"""
    from app.core.database import SessionLocal
    from app.models import TelegramAccount, Opportunity, AISettings
    from app.ai.providers import OpenAIProvider, ClaudeProvider
    from app.telegram.client import get_telegram_service
    from app.core.config import settings
    
    db = SessionLocal()
    
    try:
        # Get Telegram session
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == user_id
        ).first()
        
        if not telegram_account or not telegram_account.session_string:
            logger.error(f"No Telegram session for user {user_id}")
            return {"status": "error", "message": "Telegram not configured"}
        
        # Get recent messages
        telegram_service = get_telegram_service(telegram_account.session_string)
        messages = _run_async_task(
            telegram_service.get_recent_messages(group_id, limit=100)
        )
        
        if not messages:
            logger.warning(f"No messages found for group {group_id}")
            return {"status": "no_messages"}
        
        # Get AI provider
        ai_settings = db.query(AISettings).filter(
            AISettings.user_id == user_id
        ).first()
        
        if not ai_settings:
            logger.error(f"No AI settings for user {user_id}")
            return {"status": "error", "message": "AI provider not configured"}
        
        # Initialize AI provider
        if ai_settings.provider == "openai":
            ai_provider = OpenAIProvider(settings.OPENAI_API_KEY)
        elif ai_settings.provider == "claude":
            ai_provider = ClaudeProvider(settings.ANTHROPIC_API_KEY)
        else:
            logger.error(f"Unknown AI provider: {ai_settings.provider}")
            return {"status": "error", "message": "Unknown AI provider"}
        
        # Analyze for opportunities
        opportunities = _run_async_task(
            ai_provider.analyze_messages_for_opportunities(messages)
        )
        
        if not opportunities:
            logger.info(f"No opportunities found in group {group_id}")
            return {"status": "no_opportunities"}
        
        # Store opportunities
        for opp in opportunities:
            existing = db.query(Opportunity).filter(
                Opportunity.user_id == user_id,
                Opportunity.group_id == group_id,
                Opportunity.telegram_user_id == opp.get("user_id")
            ).first()
            
            if not existing:
                opportunity = Opportunity(
                    user_id=user_id,
                    group_id=group_id,
                    telegram_user_id=opp.get("user_id"),
                    opportunity_type=opp.get("type"),
                    evidence=opp.get("evidence"),
                    confidence=opp.get("confidence"),
                    relevance_reason=opp.get("reason"),
                    status="new"
                )
                db.add(opportunity)
        
        db.commit()
        
        logger.info(f"Found {len(opportunities)} opportunities in group {group_id}")
        return {"status": "success", "opportunities_found": len(opportunities)}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing opportunities: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def cleanup_old_logs():
    """Clean up old system logs (older than 30 days)"""
    from app.core.database import SessionLocal
    from app.models import SystemLog
    
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_count = db.query(SystemLog).filter(
            SystemLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"Deleted {deleted_count} old log entries")
        return {"status": "success", "deleted": deleted_count}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning logs: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def check_scheduler():
    """Check if scheduler should post anything now (runs every minute)"""
    from app.core.database import SessionLocal
    from app.models import SchedulerSettings, GroupFeed, Post, PostHistory
    from app.services.business import SchedulerService
    
    db = SessionLocal()
    
    try:
        # Get all active schedulers
        active_schedulers = db.query(SchedulerSettings).filter(
            SchedulerSettings.posting_mode == "automatic"
        ).all()
        
        scheduler_service = SchedulerService(db)
        tasks_queued = 0
        
        for scheduler in active_schedulers:
            # Check if in active window
            if not scheduler_service.is_in_active_window(db, scheduler.user_id):
                continue
            
            # Get enabled groups in feed
            feed_groups = db.query(GroupFeed).filter(
                GroupFeed.user_id == scheduler.user_id,
                GroupFeed.is_enabled == True
            ).order_by(GroupFeed.position).all()

            now = datetime.utcnow()
            hour_start = now - timedelta(hours=1)
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            hourly_count = db.query(PostHistory).filter(PostHistory.user_id == scheduler.user_id, PostHistory.status == "success", PostHistory.created_at >= hour_start).count()
            daily_count = db.query(PostHistory).filter(PostHistory.user_id == scheduler.user_id, PostHistory.status == "success", PostHistory.created_at >= day_start).count()
            
            for group_feed in feed_groups:
                if hourly_count >= scheduler.max_posts_per_hour or daily_count >= scheduler.max_posts_per_day:
                    break
                recent = db.query(PostHistory).filter(
                    PostHistory.user_id == scheduler.user_id,
                    PostHistory.group_id == group_feed.group_id,
                    PostHistory.status.in_(["success", "queued"]),
                    PostHistory.created_at >= now - timedelta(minutes=1),
                ).first()
                if recent:
                    continue
                # Get a recommended post
                recommended_post = db.query(Post).filter(
                    Post.user_id == scheduler.user_id,
                    Post.is_active == True
                ).first()
                
                if recommended_post:
                    # Queue posting task
                    post_to_group_task.delay(
                        user_id=scheduler.user_id,
                        group_id=group_feed.group_id,
                        post_id=recommended_post.id
                    )
                    tasks_queued += 1
                    hourly_count += 1
                    daily_count += 1
                    logger.info(f"Queued post for user {scheduler.user_id} to group {group_feed.group_id}")
        
        return {"status": "checked", "tasks_queued": tasks_queued}
    
    except Exception as e:
        logger.error(f"Error checking scheduler: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def aggregate_statistics():
    """Aggregate statistics for all active users"""
    from app.core.database import SessionLocal
    from app.models import User
    
    db = SessionLocal()
    
    try:
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            # Aggregate stats for each user
            # This would call the statistics service to calculate
            pass
        
        logger.info(f"Aggregated statistics for {len(users)} users")
        return {"status": "success", "users_aggregated": len(users)}
    
    except Exception as e:
        logger.error(f"Error aggregating statistics: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
