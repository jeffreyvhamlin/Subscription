from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Subscription, Notification
from ml.forecaster import forecast_balance
from ml.periodicity_detector import calculate_monthly_subscription_cost

def generate_plain_language_alert(user_id: int, db: Session):
    """
    Generate plain-language alerts about upcoming subscriptions and cash flow risks
    
    Example: "Your Spotify + Prime + Gym will cost ₹4,320 this month. 
              Cancelling Gym saves ₹1,200. Risk of low balance on 26th."
    """
    # Get active subscriptions
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active"
    ).all()
    
    if not subscriptions:
        return None
    
    # Get subscriptions due in next 30 days
    upcoming = []
    now = datetime.now()
    
    for sub in subscriptions:
        if sub.next_payment_date and sub.next_payment_date <= now + timedelta(days=30):
            upcoming.append(sub)
    
    if not upcoming:
        return None
    
    # Build message
    subscription_names = [sub.name for sub in upcoming]
    total_cost = sum(sub.amount for sub in upcoming)
    
    # Build alert message
    if len(subscription_names) == 1:
        message = f"Your {subscription_names[0]} subscription will cost ₹{total_cost:,.0f} soon"
    elif len(subscription_names) == 2:
        message = f"Your {subscription_names[0]} + {subscription_names[1]} will cost ₹{total_cost:,.0f} this month"
    else:
        first_names = ' + '.join(subscription_names[:3])
        message = f"Your {first_names} will cost ₹{total_cost:,.0f} this month"
    
    # Get forecast to check for low balance
    forecast = forecast_balance(user_id, db)
    
    if forecast['low_balance_dates']:
        first_low_date = forecast['low_balance_dates'][0]
        date_obj = datetime.strptime(first_low_date, '%Y-%m-%d')
        day = date_obj.day
        message += f". ⚠️ Risk of low balance on {day}th"
        alert_type = "warning"
    else:
        alert_type = "info"
    
    # Add savings opportunity for most expensive subscription
    if len(upcoming) > 1:
        most_expensive = max(upcoming, key=lambda x: x.amount)
        message += f". Cancelling {most_expensive.name} saves ₹{most_expensive.amount:,.0f}"
        alert_type = "savings_opportunity"
    
    return message, alert_type

def create_notification(user_id: int, message: str, notification_type: str, db: Session):
    """Create a notification in the database"""
    notification = Notification(
        user_id=user_id,
        message=message,
        type=notification_type
    )
    db.add(notification)
    db.commit()
    return notification

def send_email_notification(user_email: str, message: str):
    """
    Send email notification using SendGrid
    (Placeholder - requires SendGrid API key)
    """
    # TODO: Implement SendGrid integration
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    
    # For now, just log
    print(f"Email to {user_email}: {message}")
    
def check_and_notify_user(user_id: int, user_email: str, db: Session):
    """
    Check for alerts and send notifications
    Called by scheduler
    """
    result = generate_plain_language_alert(user_id, db)
    
    if result:
        message, alert_type = result
        
        # Create in-app notification
        create_notification(user_id, message, alert_type, db)
        
        # Send email notification
        send_email_notification(user_email, message)
        
        return message
    
    return None
