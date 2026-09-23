"""
Groups API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import TelegramGroup, GroupAnalysis, TelegramAccount, GroupFeed, User, AISettings
from app.schemas import GroupSearchResult, GroupAnalysisResponse
from app.api.auth import get_current_user
from app.telegram.client import get_telegram_service
from app.workers.implementations import analyze_group_task
from typing import List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AddGroupRequest(BaseModel):
    group_id: int
    name: str
    username: Optional[str] = None
    telegram_id: int


@router.get("/search", response_model=List[GroupSearchResult])
async def search_groups(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for Telegram groups by keywords.
    Requires Telegram to be connected.
    """
    try:
        # Get user's Telegram account
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == current_user.id
        ).first()
        
        if not telegram_account or not telegram_account.session_string:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Telegram account not connected"
            )
        
        # Search groups via Telegram
        telegram_service = get_telegram_service(telegram_account.session_string)
        results = await telegram_service.search_groups(q, limit=limit)
        
        logger.info(f"User {current_user.id} searched for '{q}' ({len(results)} results)")
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Group search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search groups"
        )


@router.get("/{group_id}", response_model=GroupSearchResult)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get group details"""
    try:
        group = db.query(TelegramGroup).filter(
            TelegramGroup.id == group_id,
            TelegramGroup.users.any(id=current_user.id)
        ).first()
        
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        return {
            "telegram_group_id": group.telegram_group_id,
            "name": group.name,
            "username": group.username,
            "description": group.description,
            "member_count": group.member_count or 0,
            "is_public": group.is_public,
            "already_joined": True,
            "last_analyzed": group.analysis.analyzed_at if group.analysis else None,
            "analysis": None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group: {e}")
        raise HTTPException(status_code=500, detail="Failed to get group")


@router.post("/{group_id}/analyze")
async def analyze_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger AI analysis of a group.
    Runs asynchronously via Celery worker.
    """
    try:
        # Check if group exists
        group = db.query(TelegramGroup).filter(
            TelegramGroup.id == group_id,
            TelegramGroup.users.any(id=current_user.id)
        ).first()
        
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if already analyzed recently
        recent_analysis = db.query(GroupAnalysis).filter(
            GroupAnalysis.group_id == group_id,
            GroupAnalysis.user_id == current_user.id
        ).first()
        
        if recent_analysis:
            return {
                "status": "already_analyzed",
                "analysis": {
                    "partnership_suitability": recent_analysis.partnership_suitability,
                    "job_suitability": recent_analysis.job_suitability,
                    "confidence_score": recent_analysis.confidence_score,
                    "posting_style": recent_analysis.posting_style.split(",") if recent_analysis.posting_style else [],
                }
            }
        
        # Queue Celery task
        task = analyze_group_task.delay(
            user_id=current_user.id,
            group_id=group_id
        )
        
        logger.info(f"Queued analysis for group {group_id}")
        return {"status": "analysis_queued", "task_id": task.id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing group: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze group")


@router.post("/{group_id}/add-to-feed")
async def add_group_to_feed(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a group to user's feed list"""
    try:
        group = db.query(TelegramGroup).filter(
            TelegramGroup.id == group_id,
            TelegramGroup.users.any(id=current_user.id)
        ).first()
        
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if already in feed
        existing = db.query(GroupFeed).filter(
            GroupFeed.user_id == current_user.id,
            GroupFeed.group_id == group_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Group already in feed")
        
        # Get max position
        max_position = db.query(GroupFeed).filter(
            GroupFeed.user_id == current_user.id
        ).count()
        
        # Add to feed
        feed_item = GroupFeed(
            user_id=current_user.id,
            group_id=group_id,
            position=max_position,
            is_enabled=True
        )
        db.add(feed_item)
        db.commit()
        
        logger.info(f"Added group {group_id} to user {current_user.id}'s feed")
        return {"status": "added_to_feed"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding group to feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to add group to feed")


@router.post("/manual-add")
async def manually_add_group(
    request: AddGroupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually add a group by Telegram group ID"""
    try:
        # Check if already exists
        existing = db.query(TelegramGroup).filter(
            TelegramGroup.users.any(id=current_user.id),
            TelegramGroup.telegram_group_id == str(request.telegram_id)
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Group already added")
        
        # Create group record
        group = TelegramGroup(
            name=request.name,
            username=request.username,
            telegram_id=request.telegram_id,
            is_public=bool(request.username),
            member_count=0,
            is_verified=False,
            description=""
        )
        db.add(group)
        db.flush()
        group.users.append(current_user)
        
        # Add to feed
        feed_item = GroupFeed(
            user_id=current_user.id,
            group_id=group.id,
            position=0,
            is_enabled=True
        )
        db.add(feed_item)
        db.commit()
        
        logger.info(f"Manually added group {group.id} for user {current_user.id}")
        return {"status": "group_added", "group_id": group.id}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding group manually: {e}")
        raise HTTPException(status_code=500, detail="Failed to add group")
