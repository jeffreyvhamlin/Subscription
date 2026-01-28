import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Transaction, Subscription

def forecast_balance(user_id: int, db: Session, days_ahead: int = 30):
    """
    Forecast balance for the next N days
    
    Returns:
        BalanceForecast with dates, predicted balances, and low balance warnings
    """
    # Get transaction history
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.date).all()
    
    if not transactions:
        return {
            "dates": [],
            "predicted_balance": [],
            "low_balance_dates": []
        }
    
    # Create daily balance series from transactions
    df = pd.DataFrame([
        {'date': t.date, 'amount': t.amount} 
        for t in transactions
    ])
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by date and sum amounts
    daily_df = df.groupby('date')['amount'].sum().reset_index()
    daily_df = daily_df.sort_values('date')
    
    # Calculate cumulative balance (assuming starting balance is the first cumulative sum)
    daily_df['balance'] = daily_df['amount'].cumsum()
    
    # Get current balance
    current_balance = daily_df['balance'].iloc[-1] if len(daily_df) > 0 else 0
    last_date = daily_df['date'].iloc[-1] if len(daily_df) > 0 else datetime.now()
    
    # Get upcoming subscriptions
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active"
    ).all()
    
    # Create forecast
    forecast_dates = []
    forecast_balances = []
    
    current_date = datetime.now()
    balance = current_balance
    
    for i in range(days_ahead):
        forecast_date = current_date + timedelta(days=i)
        forecast_dates.append(forecast_date.strftime('%Y-%m-%d'))
        
        # Check for subscriptions due on this date
        for sub in subscriptions:
            if sub.next_payment_date and sub.next_payment_date.date() == forecast_date.date():
                balance -= sub.amount
        
        forecast_balances.append(round(balance, 2))
    
    # Identify low balance dates (balance < 1000 or negative)
    low_balance_threshold = 1000
    low_balance_dates = [
        date for date, bal in zip(forecast_dates, forecast_balances) 
        if bal < low_balance_threshold
    ]
    
    return {
        "dates": forecast_dates,
        "predicted_balance": forecast_balances,
        "low_balance_dates": low_balance_dates
    }

def calculate_average_monthly_income(user_id: int, db: Session) -> float:
    """Calculate average monthly income from credit transactions"""
    # Get last 3 months of credit transactions
    three_months_ago = datetime.now() - timedelta(days=90)
    
    income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.amount > 0,  # Credits
        Transaction.date >= three_months_ago
    ).scalar() or 0.0
    
    return income / 3  # Average per month

def calculate_average_monthly_expenses(user_id: int, db: Session) -> float:
    """Calculate average monthly expenses from debit transactions"""
    # Get last 3 months of debit transactions
    three_months_ago = datetime.now() - timedelta(days=90)
    
    expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.amount < 0,  # Debits
        Transaction.date >= three_months_ago
    ).scalar() or 0.0
    
    return abs(expenses) / 3  # Average per month
