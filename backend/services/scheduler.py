from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from services.notification_service import check_and_notify_user

def check_all_users_notifications():
    """
    Check all users for notifications
    Called by scheduler
    """
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            check_and_notify_user(user.id, user.email, db)
    finally:
        db.close()

def init_scheduler():
    """
    Initialize APScheduler with background jobs
    """
    scheduler = BackgroundScheduler()
    
    # Daily check at 9 AM for notifications
    scheduler.add_job(
        check_all_users_notifications,
        trigger=CronTrigger(hour=9, minute=0),
        id='daily_notification_check',
        name='Check and send daily notifications',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler started successfully")
    
    return scheduler
