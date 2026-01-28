import pandas as pd
import io
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models import Transaction

async def process_csv_file(file: UploadFile, user_id: int, db: Session):
    """
    Process uploaded CSV file and save transactions to database
    
    Expected CSV format:
    Date, Description, Amount
    or
    Date, Description, Debit, Credit
    """
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()
    
    # Handle different CSV formats
    if 'amount' in df.columns:
        # Simple format: Date, Description, Amount
        df.rename(columns={'amount': 'amt'}, inplace=True)
    elif 'debit' in df.columns and 'credit' in df.columns:
        # Bank format: Date, Description, Debit, Credit
        df['amt'] = df.apply(
            lambda row: -float(row['debit']) if pd.notna(row['debit']) and str(row['debit']).strip() != '' 
            else (float(row['credit']) if pd.notna(row['credit']) and str(row['credit']).strip() != '' else 0),
            axis=1
        )
    else:
        raise ValueError("CSV must have 'Amount' column or 'Debit' and 'Credit' columns")
    
    # Parse date
    if 'date' not in df.columns:
        raise ValueError("CSV must have 'Date' column")
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Clean description
    if 'description' not in df.columns:
        raise ValueError("CSV must have 'Description' column")
    
    df['description'] = df['description'].str.strip()
    
    # Remove duplicates (same date, description, amount)
    df = df.drop_duplicates(subset=['date', 'description', 'amt'])
    
    # Save to database
    transactions = []
    for _, row in df.iterrows():
        # Check if transaction already exists
        existing = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.date == row['date'],
            Transaction.description == row['description'],
            Transaction.amount == row['amt']
        ).first()
        
        if not existing:
            transaction = Transaction(
                user_id=user_id,
                date=row['date'],
                description=row['description'],
                amount=row['amt']
            )
            db.add(transaction)
            transactions.append(transaction)
    
    db.commit()
    
    return transactions
