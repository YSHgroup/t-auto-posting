"""
Posts API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Post, TelegramGroup
from app.schemas import PostCreate, PostUpdate, PostResponse, ManualPostRequest
from typing import List
from app.api.auth import get_current_user
from app.models import User
import json

def _post_response(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "post_type": post.post_type,
        "tags": json.loads(post.tags) if post.tags else None,
        "links": json.loads(post.links) if post.links else None,
        "is_active": post.is_active,
        "created_at": post.created_at,
    }

router = APIRouter()

@router.get("", response_model=List[PostResponse])
async def list_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get all posts for current user"""
    posts = db.query(Post).filter(
        Post.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [_post_response(post) for post in posts]

@router.post("", response_model=PostResponse)
async def create_post(
    request: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    post = Post(
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        post_type=request.post_type,
        tags=json.dumps(request.tags) if request.tags else None,
        links=json.dumps(request.links) if request.links else None,
        is_active=True
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return _post_response(post)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific post"""
    post = db.query(Post).filter(
        (Post.id == post_id) & (Post.user_id == current_user.id)
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    request: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a post"""
    post = db.query(Post).filter(
        (Post.id == post_id) & (Post.user_id == current_user.id)
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if request.title is not None:
        post.title = request.title
    if request.content is not None:
        post.content = request.content
    if request.post_type is not None:
        post.post_type = request.post_type
    if request.tags is not None:
        post.tags = json.dumps(request.tags)
    if request.links is not None:
        post.links = json.dumps(request.links)
    if request.is_active is not None:
        post.is_active = request.is_active
    
    db.commit()
    db.refresh(post)
    
    return _post_response(post)

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    post = db.query(Post).filter(
        (Post.id == post_id) & (Post.user_id == current_user.id)
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return {"status": "deleted"}

@router.post("/{post_id}/duplicate", response_model=PostResponse)
async def duplicate_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Duplicate an existing post"""
    original_post = db.query(Post).filter(
        (Post.id == post_id) & (Post.user_id == current_user.id)
    ).first()
    
    if not original_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    duplicate = Post(
        user_id=current_user.id,
        title=f"{original_post.title} (Copy)",
        content=original_post.content,
        post_type=original_post.post_type,
        tags=original_post.tags,
        links=original_post.links,
        is_active=True
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return _post_response(duplicate)

@router.post("/{post_id}/send")
async def send_post(
    post_id: int,
    request: ManualPostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Queue a post for immediate delivery to one of the user's groups."""
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    group = db.query(TelegramGroup).join(TelegramGroup.users).filter(
        TelegramGroup.id == request.group_id,
        User.id == current_user.id,
    ).first()
    if not post or not post.is_active:
        raise HTTPException(status_code=404, detail="Active post not found")
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    from app.workers.implementations import post_to_group_task
    task = post_to_group_task.delay(current_user.id, group.id, post.id)
    return {"status": "queued", "task_id": task.id, "post_id": post.id, "group_id": group.id}
