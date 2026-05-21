from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "nepse_sentiment_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kathmandu",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_routes={
        "app.tasks.scraping_tasks.*": {"queue": "scraping"},
    },
)

celery_app.autodiscover_tasks(
    [
        "app.tasks.scraping_tasks",
    ]
)