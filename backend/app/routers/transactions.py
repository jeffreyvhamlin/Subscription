from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import User, Transaction
from app.schemas import TransactionResponse, TransactionStats, BalanceForecast
from app.auth import get_current_user
from services.transaction_processor import process_csv_file
from ml.periodicity_detector import detect_subscriptions
from ml.forecaster import forecast_balance

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_transactions(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a CSV file of bank transactions"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    try:
        # Process CSV and save transactions
        transactions = await process_csv_file(file, current_user.id, db)
        
        # Run subscription detection
        detect_subscriptions(current_user.id, db)
        
        return {
            "message": f"Successfully uploaded {len(transactions)} transactions",
            "transactions_count": len(transactions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transactions"""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    
    return transactions

@router.get("/stats", response_model=TransactionStats)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction statistics"""
    from sqlalchemy import func
    from ml.periodicity_detector import calculate_monthly_subscription_cost
    
    # Total transactions
    total_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).count()
    
    # Total subscriptions
    from app.models import Subscription
    total_subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).count()
    
    # Monthly subscription cost
    monthly_cost = calculate_monthly_subscription_cost(current_user.id, db)
    
    # Total spent this month
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_spent_this_month = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= current_month_start,
        Transaction.amount < 0  # Only debits
    ).scalar() or 0.0
    
    # Total spent overall (lifetime)
    total_spent_overall = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.amount < 0  # Only debits
    ).scalar() or 0.0
    
    # Average spent per month
    # Get number of months between first transaction and now
    first_transaction_date = db.query(func.min(Transaction.date)).filter(
        Transaction.user_id == current_user.id
    ).scalar()
    
    if first_transaction_date:
        now = datetime.now()
        num_months = (now.year - first_transaction_date.year) * 12 + (now.month - first_transaction_date.month) + 1
        avg_spent_per_month = total_spent_overall / num_months
    else:
        avg_spent_per_month = 0.0
    
    return {
        "total_transactions": total_transactions,
        "total_subscriptions": total_subscriptions,
        "monthly_subscription_cost": abs(monthly_cost),
        "total_spent_this_month": abs(total_spent_this_month),
        "avg_spent_per_month": abs(avg_spent_per_month),
        "total_spent_overall": abs(total_spent_overall)
    }

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all transactions, subscriptions, and notifications for the current user"""
    from app.models import Subscription, Notification
    
    try:
        # Delete transactions
        db.query(Transaction).filter(Transaction.user_id == current_user.id).delete(synchronize_session=False)
        # Delete subscriptions
        db.query(Subscription).filter(Subscription.user_id == current_user.id).delete(synchronize_session=False)
        # Delete notifications
        db.query(Notification).filter(Notification.user_id == current_user.id).delete(synchronize_session=False)
        
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing data: {str(e)}"
        )

@router.get("/forecast", response_model=BalanceForecast)
def get_forecast(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get balance forecast for next 30 days"""
    forecast = forecast_balance(current_user.id, db)
    return forecast
