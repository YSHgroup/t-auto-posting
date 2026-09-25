"""
Feed management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import GroupFeed, TelegramGroup, PostHistory, Reply
from app.schemas import FeedItem, FeedReorderRequest
from typing import List
from app.api.auth import get_current_user
from app.models import User
from app.core.config import settings
import json

router = APIRouter()

@router.get("", response_model=List[FeedItem])
async def get_feed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's group feed in order"""
    feed_items = db.query(GroupFeed).filter(
        GroupFeed.user_id == current_user.id
    ).order_by(GroupFeed.position).all()
    
    return [{
        "id": item.id,
        "position": item.position,
        "group_name": item.group.name,
        "group_username": item.group.username,
        "member_count": item.group.member_count or 0,
        "is_enabled": item.is_enabled,
        "category": None,
        "last_post_at": None,
        "next_scheduled_post": None,
        "post_count": db.query(PostHistory).filter(PostHistory.user_id == current_user.id, PostHistory.group_id == item.group_id, PostHistory.status == "success").count(),
        "reply_count": db.query(Reply).filter(Reply.user_id == current_user.id, Reply.group_id == item.group_id).count(),
    } for item in feed_items]

@router.post("/add")
async def add_to_feed(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add group to feed"""
    group_id = request.get("group_id")
    group = db.query(TelegramGroup).filter(TelegramGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if already in feed
    existing = db.query(GroupFeed).filter(
        (GroupFeed.user_id == current_user.id) & 
        (GroupFeed.group_id == group_id)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Group already in feed")
    
    # Get max position
    max_position = db.query(GroupFeed).filter(
        GroupFeed.user_id == current_user.id
    ).order_by(GroupFeed.position.desc()).first()
    
    new_position = (max_position.position + 1) if max_position else 1
    
    feed_item = GroupFeed(
        user_id=current_user.id,
        group_id=group_id,
        position=new_position,
        is_enabled=True
    )
    
    db.add(feed_item)
    db.commit()
    db.refresh(feed_item)
    
    return {"status": "added", "feed_item_id": feed_item.id}

@router.put("/reorder")
async def reorder_feed(
    request: FeedReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reorder feed items"""
    for item in request.items:
        feed_item = db.query(GroupFeed).filter(
            (GroupFeed.id == item["id"]) &
            (GroupFeed.user_id == current_user.id)
        ).first()
        
        if feed_item:
            feed_item.position = item["position"]
    
    db.commit()
    return {"status": "reordered"}

@router.put("/{feed_item_id}/toggle")
async def toggle_feed_item(
    feed_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable/disable a feed item"""
    feed_item = db.query(GroupFeed).filter(
        (GroupFeed.id == feed_item_id) &
        (GroupFeed.user_id == current_user.id)
    ).first()
    
    if not feed_item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    
    feed_item.is_enabled = not feed_item.is_enabled
    db.commit()
    
    return {"status": "toggled", "is_enabled": feed_item.is_enabled}

@router.delete("/{feed_item_id}")
async def remove_from_feed(
    feed_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove group from feed"""
    feed_item = db.query(GroupFeed).filter(
        (GroupFeed.id == feed_item_id) &
        (GroupFeed.user_id == current_user.id)
    ).first()
    
    if not feed_item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    
    db.delete(feed_item)
    db.commit()
    
    return {"status": "removed"}

@router.get("/{feed_item_id}/recommendations")
async def get_post_recommendations(
    feed_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI post recommendations for a group"""
    feed_item = db.query(GroupFeed).filter(
        (GroupFeed.id == feed_item_id) &
        (GroupFeed.user_id == current_user.id)
    ).first()
    
    if not feed_item:
        raise HTTPException(status_code=404, detail="Feed item not found")
    
    from app.models import Post, GroupAnalysis, AISettings
    posts = db.query(Post).filter(Post.user_id == current_user.id, Post.is_active == True).all()
    if not posts:
        return {"recommendations": []}
    analysis = db.query(GroupAnalysis).filter(GroupAnalysis.group_id == feed_item.group_id).first()
    ai_settings = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
    analysis_data = {}
    if analysis and analysis.analysis_text:
        try:
            analysis_data = json.loads(analysis.analysis_text)
        except json.JSONDecodeError:
            analysis_data = {"analysis": analysis.analysis_text}

    recommendation = None
    if ai_settings:
        from app.ai.providers import OpenAIProvider, ClaudeProvider
        provider = OpenAIProvider(settings.OPENAI_API_KEY, ai_settings.model) if ai_settings.provider == "openai" else ClaudeProvider(settings.ANTHROPIC_API_KEY, ai_settings.model)
        recommendation = await provider.recommend_post(
            analysis_data,
            [{"id": post.id, "title": post.title, "content": post.content, "type": post.post_type} for post in posts],
        )

    recommended_id = recommendation.get("recommended_post_id") if recommendation else None
    selected = next((post for post in posts if post.id == recommended_id), posts[0])
    alternatives = recommendation.get("alternatives", []) if recommendation else []
    return {"recommendations": [{
        "group_id": feed_item.group_id,
        "group_name": feed_item.group.name,
        "recommended_post_id": selected.id,
        "recommended_post_title": selected.title,
        "reason": recommendation.get("reason", "Selected from active posts; analyze the group to improve matching.") if recommendation else "Selected from active posts; analyze the group to improve matching.",
        "compatibility_score": recommendation.get("compatibility_score", 50) if recommendation else (analysis.confidence_score if analysis else 50),
        "alternative_posts": [{"id": post.id, "title": post.title} for post in posts if post.id in alternatives][:5],
    }]}
