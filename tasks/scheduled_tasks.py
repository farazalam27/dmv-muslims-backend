from celery import Celery
from celery.schedules import crontab
from config import settings
import logging
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

# Register periodic tasks
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up periodic tasks to run at specific times"""
    
    # Daily scraping job at the configured hour (default: 2 AM)
    sender.add_periodic_task(
        crontab(hour=settings.SCRAPER_RUN_HOUR, minute=0),
        daily_scraping_job.s(),
        name="daily-scraping-job",
    )
    
    # Health check every hour
    sender.add_periodic_task(
        crontab(minute=0, hour="*/1"),
        health_check.s(),
        name="hourly-health-check",
    )

@celery_app.task
def daily_scraping_job():
    """Run all scrapers daily"""
    logger.info("Starting daily scraping job")
    
    # This will be implemented when we create the orchestrator
    # orchestrator = Orchestrator()
    # results = asyncio.run(orchestrator.run_all_agents(region=settings.DEFAULT_REGION))
    
    # For now, just log that it would run
    logger.info(f"Would run scrapers for region: {settings.DEFAULT_REGION}")
    
    return {"status": "completed", "message": "Daily scraping job completed"}

@celery_app.task
def health_check():
    """Periodic health check to ensure system is running"""
    logger.info("Running health check")
    
    # Check database connection
    # This will be implemented when we create the health check logic
    
    return {"status": "healthy", "timestamp": "now"}