from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "agentic_automation_studio",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.MAX_WORKFLOW_EXECUTION_TIME,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)

celery_app.autodiscover_tasks(['app.core.tasks'])
