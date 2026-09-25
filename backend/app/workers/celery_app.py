"""Celery application and periodic task configuration."""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "telegram_intelligence",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "check-scheduler-every-minute": {
        "task": "app.workers.implementations.check_scheduler",
        "schedule": crontab(minute="*/1"),
    },
    "monitor-replies-every-five-minutes": {
        "task": "app.workers.implementations.monitor_replies_task",
        "schedule": crontab(minute="*/5"),
    },
    "cleanup-old-logs-daily": {
        "task": "app.workers.implementations.cleanup_old_logs",
        "schedule": crontab(hour=2, minute=0),
    },
    "aggregate-statistics-hourly": {
        "task": "app.workers.implementations.aggregate_statistics",
        "schedule": crontab(minute=0),
    },
}

# Register the task decorators when Celery imports this module.
from app.workers import implementations  # noqa: E402,F401
