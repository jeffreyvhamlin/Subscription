from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Subscription, Notification
from app.schemas import SubscriptionResponse, SubscriptionUpdate, NotificationResponse, UpcomingCharge
from app.auth import get_current_user

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

@router.get("", response_model=List[SubscriptionResponse])
def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all detected subscriptions"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Subscription.amount.desc()).all()
    
    return subscriptions

@router.get("/upcoming", response_model=List[UpcomingCharge])
def get_upcoming_charges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming subscription charges in next 30 days"""
    from datetime import datetime, timedelta
    
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active",
        Subscription.next_payment_date.isnot(None)
    ).all()
    
    now = datetime.now()
    upcoming = []
    
    for sub in subscriptions:
        if sub.next_payment_date and sub.next_payment_date <= now + timedelta(days=30):
            upcoming.append({
                "subscription_name": sub.name,
                "amount": sub.amount,
                "date": sub.next_payment_date
            })
    
    # Sort by date
    upcoming.sort(key=lambda x: x["date"])
    
    return upcoming

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    update: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update subscription (e.g., mark as cancelled)"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    if update.status:
        subscription.status = update.status
    
    db.commit()
    db.refresh(subscription)
    
    return subscription

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return notifications
