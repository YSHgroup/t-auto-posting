"""
Application settings and configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os
import json

class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-random-32-character-secret")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://telegram_user:telegram_password@localhost:5432/telegram_bot"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    
    # Telegram
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_PHONE_NUMBER: str = os.getenv("TELEGRAM_PHONE_NUMBER", "")
    
    # Telegram API Rate Limits
    TELEGRAM_MIN_POSTING_INTERVAL_SECONDS: int = 60  # Minimum 60 seconds between posts
    TELEGRAM_MESSAGE_THRESHOLD: int = 20  # Minimum 20 messages between previous and latest post
    TELEGRAM_SESSION_ENCRYPTION_KEY: str = os.getenv("SECRET_KEY", "default-key")
    
    # AI Providers
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DEFAULT_AI_PROVIDER: str = "openai"  # or "claude"
    DEFAULT_AI_MODEL: str = "gpt-4"  # for OpenAI
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    
    # CORS
    CORS_ORIGINS: List[str] = json.loads(os.getenv(
        "CORS_ORIGINS",
        '["http://localhost:3000", "http://localhost:8000", "chrome-extension://localhost"]',
    ))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
