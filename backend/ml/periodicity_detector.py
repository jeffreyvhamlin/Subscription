import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fuzzywuzzy import fuzz
from collections import defaultdict

from app.models import Transaction, Subscription

def group_similar_transactions(transactions):
    """
    Group transactions with similar descriptions using fuzzy matching
    Returns: dict of {group_key: [transactions]}
    """
    groups = defaultdict(list)
    processed = set()
    
    for i, trans in enumerate(transactions):
        if i in processed:
            continue
        
        # Start a new group
        group_key = trans.description[:30]  # Use first 30 chars as key
        groups[group_key].append(trans)
        processed.add(i)
        
        # Find similar transactions
        for j, other_trans in enumerate(transactions[i+1:], start=i+1):
            if j in processed:
                continue
            
            # Use fuzzy string matching
            similarity = fuzz.ratio(trans.description.lower(), other_trans.description.lower())
            
            # If very similar descriptions, group them
            if similarity > 80:
                groups[group_key].append(other_trans)
                processed.add(j)
    
    return groups

def detect_periodicity(transaction_dates, min_occurrences=3):
    """
    Detect if transactions occur at regular intervals
    Returns: (is_periodic, frequency, confidence)
    """
    if len(transaction_dates) < min_occurrences:
        return False, None, 0.0
    
    # Sort dates
    dates = sorted(transaction_dates)
    
    # Calculate intervals between consecutive transactions (in days)
    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    
    if not intervals:
        return False, None, 0.0
    
    # Check for monthly pattern (28-31 days)
    monthly_intervals = [i for i in intervals if 25 <= i <= 35]
    if len(monthly_intervals) >= len(intervals) * 0.7:  # 70% of intervals are monthly
        avg_interval = np.mean(monthly_intervals)
        std_interval = np.std(monthly_intervals) if len(monthly_intervals) > 1 else 0
        confidence = 1.0 - min(std_interval / avg_interval, 1.0) if avg_interval > 0 else 0.5
        return True, "monthly", max(confidence, 0.6)
    
    # Check for weekly pattern (6-8 days)
    weekly_intervals = [i for i in intervals if 6 <= i <= 8]
    if len(weekly_intervals) >= len(intervals) * 0.7:
        avg_interval = np.mean(weekly_intervals)
        std_interval = np.std(weekly_intervals) if len(weekly_intervals) > 1 else 0
        confidence = 1.0 - min(std_interval / avg_interval, 1.0) if avg_interval > 0 else 0.5
        return True, "weekly", max(confidence, 0.6)
    
    # Check for quarterly pattern (88-95 days)
    quarterly_intervals = [i for i in intervals if 85 <= i <= 95]
    if len(quarterly_intervals) >= len(intervals) * 0.7:
        avg_interval = np.mean(quarterly_intervals)
        std_interval = np.std(quarterly_intervals) if len(quarterly_intervals) > 1 else 0
        confidence = 1.0 - min(std_interval / avg_interval, 1.0) if avg_interval > 0 else 0.5
        return True, "quarterly", max(confidence, 0.6)
    
    return False, None, 0.0

def extract_subscription_name(description):
    """Extract a clean subscription name from transaction description"""
    # Common patterns to clean
    description = description.upper()
    
    # Known subscription keywords
    streaming = ['NETFLIX', 'SPOTIFY', 'PRIME', 'AMAZON PRIME', 'DISNEY', 'HBO', 'APPLE MUSIC']
    gym = ['GYM', 'FITNESS', 'PLANET FITNESS', 'GOLD\'S GYM']
    utilities = ['ELECTRICITY', 'WATER', 'GAS', 'INTERNET', 'MOBILE']
    
    for keyword in streaming + gym + utilities:
        if keyword in description:
            return keyword.title()
    
    # Otherwise, take first 3 words
    words = description.split()
    return ' '.join(words[:3]).title()

def detect_subscriptions(user_id: int, db: Session):
    """
    Main function to detect recurring subscriptions from transactions
    """
    # Get all user transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.amount < 0  # Only debits (expenses)
    ).all()
    
    if len(transactions) < 3:
        return []
    
    # Group similar transactions
    groups = group_similar_transactions(transactions)
    
    detected_subscriptions = []
    
    for group_key, group_transactions in groups.items():
        if len(group_transactions) < 3:
            continue
        
        # Get dates and amounts
        dates = [t.date for t in group_transactions]
        amounts = [abs(t.amount) for t in group_transactions]
        
        # Check if amounts are similar (within 10%)
        avg_amount = np.mean(amounts)
        amount_variation = np.std(amounts) / avg_amount if avg_amount > 0 else 1.0
        
        if amount_variation > 0.15:  # More than 15% variation
            continue
        
        # Detect periodicity
        is_periodic, frequency, confidence = detect_periodicity(dates)
        
        if is_periodic and confidence > 0.5:
            # Extract subscription name
            subscription_name = extract_subscription_name(group_transactions[0].description)
            
            # Calculate next payment date
            last_date = max(dates)
            if frequency == "monthly":
                next_payment = last_date + timedelta(days=30)
            elif frequency == "weekly":
                next_payment = last_date + timedelta(days=7)
            elif frequency == "quarterly":
                next_payment = last_date + timedelta(days=90)
            else:
                next_payment = None
            
            # Check if subscription already exists
            existing_sub = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.name == subscription_name
            ).first()
            
            if existing_sub:
                # Update existing subscription
                existing_sub.amount = avg_amount
                existing_sub.frequency = frequency
                existing_sub.confidence_score = confidence
                existing_sub.last_payment_date = last_date
                existing_sub.next_payment_date = next_payment
            else:
                # Create new subscription
                subscription = Subscription(
                    user_id=user_id,
                    name=subscription_name,
                    amount=avg_amount,
                    frequency=frequency,
                    confidence_score=confidence,
                    last_payment_date=last_date,
                    next_payment_date=next_payment,
                    status="active"
                )
                db.add(subscription)
                detected_subscriptions.append(subscription)
            
            # Mark transactions as recurring
            for trans in group_transactions:
                trans.is_recurring = True
    
    db.commit()
    
    return detected_subscriptions

def calculate_monthly_subscription_cost(user_id: int, db: Session) -> float:
    """Calculate total monthly cost of all active subscriptions"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active"
    ).all()
    
    total = 0.0
    for sub in subscriptions:
        if sub.frequency == "monthly":
            total += sub.amount
        elif sub.frequency == "weekly":
            total += sub.amount * 4.33  # Average weeks per month
        elif sub.frequency == "quarterly":
            total += sub.amount / 3
    
    return total
