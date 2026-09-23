"""
Database models for all entities
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    telegram_account = relationship("TelegramAccount", uselist=False, back_populates="user")
    ai_settings = relationship("AISettings", uselist=False, back_populates="user")
    posts = relationship("Post", back_populates="user")
    groups = relationship("TelegramGroup", secondary="user_groups", back_populates="users")
    feed = relationship("GroupFeed", back_populates="user")
    post_history = relationship("PostHistory", back_populates="user")
    replies = relationship("Reply", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    opportunities = relationship("Opportunity", back_populates="user")
    scheduler_settings = relationship("SchedulerSettings", uselist=False, back_populates="user")


class TelegramAccount(Base):
    """Telegram account credentials (encrypted)"""
    __tablename__ = "telegram_accounts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    phone_number = Column(String)
    telegram_id = Column(Integer, unique=True, nullable=True)
    session_string = Column(Text)  # Encrypted session
    is_active = Column(Boolean, default=False)
    connected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="telegram_account")


class AISettings(Base):
    """AI provider settings per user"""
    __tablename__ = "ai_settings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    provider = Column(String, default="openai")  # openai or claude
    api_key = Column(Text)  # Encrypted
    model = Column(String, default="gpt-4")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ai_settings")


class TelegramGroup(Base):
    """Telegram group information"""
    __tablename__ = "telegram_groups"
    
    id = Column(Integer, primary_key=True)
    telegram_group_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    username = Column(String, nullable=True, index=True)
    member_count = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    is_supergroup = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary="user_groups", back_populates="groups")
    analysis = relationship("GroupAnalysis", uselist=False, back_populates="group")
    categories = relationship("GroupCategory", secondary="group_categories", back_populates="groups")
    feed_items = relationship("GroupFeed", back_populates="group")
    post_assignments = relationship("GroupPostAssignment", back_populates="group")
    post_history = relationship("PostHistory", back_populates="group")
    replies = relationship("Reply", back_populates="group")
    opportunities = relationship("Opportunity", back_populates="group")


class GroupAnalysis(Base):
    """AI analysis results for a group"""
    __tablename__ = "group_analysis"
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("telegram_groups.id"), unique=True)
    group_types = Column(Text)  # JSON array
    partnership_suitability = Column(String)  # Suitable, Possibly, Not Recommended
    partnership_reason = Column(Text)
    job_suitability = Column(String)
    job_reason = Column(Text)
    posting_style = Column(Text)  # JSON array
    risks = Column(Text)  # JSON array
    communication_style = Column(Text)  # JSON array
    confidence_score = Column(Integer)  # 0-100
    analysis_text = Column(Text)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("TelegramGroup", back_populates="analysis")


class GroupCategory(Base):
    """Categories for grouping (developer, startup, etc)"""
    __tablename__ = "group_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    groups = relationship("TelegramGroup", secondary="group_categories", back_populates="categories")


# Association tables
user_groups = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("group_id", Integer, ForeignKey("telegram_groups.id"))
)

group_categories_table = Table(
    "group_categories",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("telegram_groups.id")),
    Column("category_id", Integer, ForeignKey("group_categories.id"))
)


class Post(Base):
    """User-created post templates"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    content = Column(Text)
    post_type = Column(String)  # Partnership, Job, Business, Investor, General, Custom
    tags = Column(Text)  # JSON array
    links = Column(Text)  # JSON array
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    group_assignments = relationship("GroupPostAssignment", back_populates="post")
    post_history = relationship("PostHistory", back_populates="post")


class GroupPostAssignment(Base):
    """Assignment of posts to groups in feed"""
    __tablename__ = "group_post_assignments"
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("telegram_groups.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    is_selected = Column(Boolean, default=False)  # Currently selected for this group
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("TelegramGroup", back_populates="post_assignments")
    post = relationship("Post", back_populates="group_assignments")


class GroupFeed(Base):
    """User's ordered feed of groups for posting"""
    __tablename__ = "group_feed"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("telegram_groups.id"))
    position = Column(Integer)  # For ordering
    is_enabled = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feed")
    group = relationship("TelegramGroup", back_populates="feed_items")


class PostHistory(Base):
    """History of all post attempts"""
    __tablename__ = "post_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("telegram_groups.id"))
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    telegram_message_id = Column(String, nullable=True)
    status = Column(String)  # Success, Skipped, Failed, Rate Limited, Unauthorized
    reason = Column(Text, nullable=True)  # Why skipped or failed
    messages_since_last = Column(Integer, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="post_history")
    group = relationship("TelegramGroup", back_populates="post_history")
    post = relationship("Post", back_populates="post_history")
    replies = relationship("Reply", back_populates="post_history")


class Reply(Base):
    """Replies to user's posts"""
    __tablename__ = "replies"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("telegram_groups.id"))
    post_history_id = Column(Integer, ForeignKey("post_history.id"), nullable=True)
    telegram_user_id = Column(String)
    telegram_user_name = Column(String, nullable=True)
    message_text = Column(Text)
    telegram_message_id = Column(String)
    received_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="replies")
    group = relationship("TelegramGroup", back_populates="replies")
    post_history = relationship("PostHistory", back_populates="replies")
    notification = relationship("Notification", uselist=False, back_populates="reply")


class Notification(Base):
    """Notifications for replies"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reply_id = Column(Integer, ForeignKey("replies.id"))
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    reply = relationship("Reply", back_populates="notification")


class Opportunity(Base):
    """Identified investment/partnership opportunities"""
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("telegram_groups.id"))
    telegram_user_id = Column(String)
    telegram_user_name = Column(String, nullable=True)
    opportunity_type = Column(String)  # Investment, Partnership
    evidence = Column(Text)  # Relevant message/context
    confidence = Column(String)  # High, Medium, Low
    relevance_reason = Column(Text)
    status = Column(String, default="new")  # new, reviewed, contacted, dismissed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="opportunities")
    group = relationship("TelegramGroup", back_populates="opportunities")


class SchedulerSettings(Base):
    """User's scheduler configuration"""
    __tablename__ = "scheduler_settings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    posting_mode = Column(String, default="manual")  # manual or automatic
    active_start_time = Column(String, default="09:00")  # HH:MM
    active_end_time = Column(String, default="20:00")
    active_days = Column(String, default="1,2,3,4,5")  # 1=Monday, 7=Sunday
    timezone = Column(String, default="UTC")
    min_messages_between_posts = Column(Integer, default=20)
    max_posts_per_hour = Column(Integer, default=5)
    max_posts_per_day = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scheduler_settings")


class SystemLog(Base):
    """System audit logs"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)
    resource = Column(String)
    details = Column(Text, nullable=True)
    status = Column(String)  # success, error, warning
    created_at = Column(DateTime, default=datetime.utcnow)
