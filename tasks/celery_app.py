from celery import Celery
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "dmv_muslims",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/New_York",
    enable_utc=True,
    worker_hijack_root_logger=False,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=1000,
)

# Import tasks to ensure they're registered
# This will be populated as we implement more tasks
celery_app.autodiscover_tasks(["tasks"])

@celery_app.task(bind=True)
def debug_task(self):
    """Test task to verify Celery is working"""
    logger.info(f"Request: {self.request!r}")
    return {"status": "Celery is working!"}