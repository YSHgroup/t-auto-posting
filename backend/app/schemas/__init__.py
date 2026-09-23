"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ============ Auth Schemas ============
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ Telegram Schemas ============
class TelegramAccountStatus(BaseModel):
    is_connected: bool
    phone_number: Optional[str] = None
    telegram_id: Optional[int] = None
    connected_at: Optional[datetime] = None

# ============ Group Schemas ============
class GroupMetadata(BaseModel):
    telegram_group_id: str
    name: str
    username: Optional[str]
    member_count: Optional[int]
    description: Optional[str]
    is_public: bool

class GroupAnalysisResponse(BaseModel):
    group_types: List[str]
    partnership_suitability: str  # Suitable, Possibly Suitable, Not Recommended
    partnership_reason: str
    job_suitability: str
    job_reason: str
    posting_style: List[str]
    risks: List[str]
    communication_style: List[str]
    confidence_score: int  # 0-100

class GroupSearchResult(BaseModel):
    telegram_group_id: str
    name: str
    username: Optional[str]
    member_count: int
    description: Optional[str]
    is_public: bool
    relevance_score: Optional[int] = None
    already_joined: bool = False
    last_analyzed: Optional[datetime] = None
    analysis: Optional[GroupAnalysisResponse] = None

# ============ Feed Schemas ============
class FeedItem(BaseModel):
    id: int
    position: int
    group_name: str
    group_username: Optional[str]
    member_count: int
    is_enabled: bool
    category: Optional[str]
    last_post_at: Optional[datetime]
    next_scheduled_post: Optional[datetime]
    post_count: int
    reply_count: int

class FeedReorderRequest(BaseModel):
    items: List[dict]  # [{id: int, position: int}]

# ============ Post Schemas ============
class PostCreate(BaseModel):
    title: str
    content: str
    post_type: str  # Partnership, Job, Business, Investor, General, Custom
    tags: Optional[List[str]] = None
    links: Optional[List[str]] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    post_type: Optional[str] = None
    tags: Optional[List[str]] = None
    links: Optional[List[str]] = None
    is_active: Optional[bool] = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    post_type: str
    tags: Optional[List[str]]
    links: Optional[List[str]]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostRecommendationResponse(BaseModel):
    group_id: int
    group_name: str
    recommended_post_id: int
    recommended_post_title: str
    reason: str
    compatibility_score: int  # 0-100
    alternative_posts: Optional[List[dict]] = None

# ============ Scheduler Schemas ============
class SchedulerConfig(BaseModel):
    posting_mode: str  # manual or automatic
    active_start_time: str  # HH:MM
    active_end_time: str
    active_days: str  # "1,2,3,4,5"
    timezone: str
    min_messages_between_posts: int
    max_posts_per_hour: int
    max_posts_per_day: int

class SchedulerStatus(BaseModel):
    is_running: bool
    posting_mode: str
    last_post_at: Optional[datetime]
    next_post_at: Optional[datetime]
    posts_today: int
    posts_this_hour: int

# ============ Notification Schemas ============
class NotificationResponse(BaseModel):
    id: int
    group_name: str
    telegram_user_name: str
    message_text: str
    received_at: datetime
    is_read: bool

# ============ Opportunity Schemas ============
class OpportunityResponse(BaseModel):
    id: int
    group_name: str
    telegram_user_name: str
    opportunity_type: str  # Investment, Partnership
    evidence: str
    confidence: str  # High, Medium, Low
    relevance_reason: str
    status: str  # new, reviewed, contacted, dismissed

# ============ Statistics Schemas ============
class StatisticsResponse(BaseModel):
    total_groups: int
    active_groups: int
    total_posts: int
    posts_this_week: int
    skipped_posts: int
    failed_posts: int
    total_replies: int
    unread_replies: int
    opportunities_identified: int
    last_post_at: Optional[datetime]
    next_scheduled_post: Optional[datetime]
