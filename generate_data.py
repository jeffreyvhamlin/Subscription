import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_transactions(num_transactions=500, years=1):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    
    data = []
    
    # --- 1. Monthly Salary (Credit) ---
    current_date = start_date.replace(day=1) + timedelta(days=30)
    while current_date <= end_date:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Description': 'CORPORATE SALARY CREDIT',
            'Debit': '',
            'Credit': 50000.00
        })
        current_date += timedelta(days=30)
        # Randomize day a bit
        current_date = current_date.replace(day=min(random.randint(28, 31), 30))

    # --- 2. Monthly Rent (Debit) ---
    current_date = start_date.replace(day=5)
    while current_date <= end_date:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Description': 'MONTHLY RENT PAYMENT',
            'Debit': 15000.00,
            'Credit': ''
        })
        current_date += timedelta(days=30)

    # --- 3. Subscriptions (Monthly) ---
    subs = [
        ('NETFLIX.COM SUBSCRIPTION', 199.00),
        ('SPOTIFY PREMIUM', 149.00),
        ('GYM MEMBERSHIP AUTOPAY', 1200.00),
        ('AMAZON PRIME VIDEO', 179.00),
        ('YOUTUBE PREMIUM', 129.00)
    ]
    
    for name, amount in subs:
        current_date = start_date + timedelta(days=random.randint(1, 28))
        while current_date <= end_date:
            # Add slight variations to description
            desc = name
            if random.random() > 0.7:
                desc = name + " REF " + str(random.randint(1000, 9999))
                
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Description': desc,
                'Debit': amount,
                'Credit': ''
            })
            current_date += timedelta(days=30)

    # --- 4. Weekly Grocery (Weekly) ---
    current_date = start_date
    while current_date <= end_date:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Description': 'SUPERMARKET GROCERIES',
            'Debit': random.uniform(800, 1500),
            'Credit': ''
        })
        current_date += timedelta(days=7)

    # --- 5. Random Transactions (Daily/Irregular) ---
    remaining = num_transactions - len(data)
    random_descs = ['UBER RIDE', 'STARBUCKS COFFEE', 'RESTAURANT DINNER', 'ZOMATO ORDER', 
                    'AMAZON SHOPPING', 'PHARMACY', 'MOVIE TICKETS', 'PETROL PUMP', 
                    'LAUNDRY SERVICE', 'BOOKSTORE']
    
    for _ in range(remaining):
        random_date = start_date + timedelta(days=random.randint(0, 365))
        if random_date > end_date: continue
        
        data.append({
            'Date': random_date.strftime('%Y-%m-%d'),
            'Description': random.choice(random_descs),
            'Debit': round(random.uniform(50, 2000), 2),
            'Credit': ''
        })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    # Ensure numerical formatting
    df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce')
    df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce')
    
    return df

if __name__ == "__main__":
    df = generate_transactions(500)
    df.to_csv('data/transactions_1year.csv', index=False)
    print(f"Generated {len(df)} transactions in data/transactions_1year.csv")
