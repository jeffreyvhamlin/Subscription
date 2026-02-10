import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_transactions(start_date=None, end_date=None, monthly_salary=50000.0, num_random_transactions=500):
    """
    Generate synthetic bank transactions between start_date and end_date.
    
    Args:
        start_date (str or datetime): Start of transaction history (e.g., '2023-01-01')
        end_date (str or datetime): End of transaction history (defaults to now)
        monthly_salary (float): Recurring salary credit amount
        num_random_transactions (int): Number of irregular/random transactions to sprinkle in
    """
    # Handle dates
    if end_date is None:
        end_date = datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    if start_date is None:
        start_date = end_date - timedelta(days=365)
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    total_days = (end_date - start_date).days
    if total_days <= 0:
        raise ValueError("Start date must be before end date")

    data = []
    
    # --- 1. Monthly Salary (Credit) ---
    # First salary pay day after start_date
    current_date = start_date.replace(day=min(random.randint(1, 5), 28))
    if current_date < start_date:
        current_date += timedelta(days=30)
        
    while current_date <= end_date:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Description': 'CORPORATE SALARY CREDIT',
            'Debit': '',
            'Credit': float(monthly_salary)
        })
        # Move to next month
        next_month = current_date.month + 1
        next_year = current_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        current_date = current_date.replace(year=next_year, month=next_month, day=min(random.randint(1, 5), 28))

    # --- 2. Monthly Rent (Debit) ---
    current_date = start_date.replace(day=min(random.randint(5, 10), 28))
    if current_date < start_date:
        current_date += timedelta(days=30)

    while current_date <= end_date:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Description': 'MONTHLY RENT PAYMENT',
            'Debit': 15000.00,
            'Credit': ''
        })
        # Move to next month
        next_month = current_date.month + 1
        next_year = current_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        current_date = current_date.replace(year=next_year, month=next_month, day=min(random.randint(5, 10), 28))

    # --- 3. Subscriptions (Monthly) ---
    subs = [
        ('NETFLIX.COM SUBSCRIPTION', 199.00),
        ('SPOTIFY PREMIUM', 149.00),
        ('GYM MEMBERSHIP AUTOPAY', 1200.00),
        ('AMAZON PRIME VIDEO', 179.00),
        ('YOUTUBE PREMIUM', 129.00)
    ]
    
    for name, amount in subs:
        # Each sub has its own fixed day of the month
        sub_day = random.randint(1, 28)
        current_date = start_date.replace(day=sub_day)
        if current_date < start_date:
            current_date += timedelta(days=30)

        while current_date <= end_date:
            # Add slight variations to description
            desc = name
            if random.random() > 0.8:
                desc = name + " REF " + str(random.randint(1000, 9999))
                
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Description': desc,
                'Debit': amount,
                'Credit': ''
            })
            # Move to next month
            next_month = current_date.month + 1
            next_year = current_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            current_date = current_date.replace(year=next_year, month=next_month, day=sub_day)

    # --- 4. Weekly Grocery (Weekly) ---
    current_date = start_date
    while current_date <= end_date:
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Description': 'SUPERMARKET GROCERIES',
            'Debit': round(random.uniform(800, 2500), 2),
            'Credit': ''
        })
        current_date += timedelta(days=7)

    # --- 5. Random Transactions (Irregular) ---
    random_descs = ['UBER RIDE', 'STARBUCKS COFFEE', 'RESTAURANT DINNER', 'ZOMATO ORDER', 
                    'AMAZON SHOPPING', 'PHARMACY', 'MOVIE TICKETS', 'PETROL PUMP', 
                    'LAUNDRY SERVICE', 'BOOKSTORE', 'CLOTHING STORE', 'LOCAL TEA STALL']
    
    for _ in range(num_random_transactions):
        random_day_offset = random.randint(0, total_days)
        random_date = start_date + timedelta(days=random_day_offset)
        
        data.append({
            'Date': random_date.strftime('%Y-%m-%d'),
            'Description': random.choice(random_descs),
            'Debit': round(random.uniform(20, 3000), 2),
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
    # Example Usage:
    # 2 years of data, 75k salary
    start = '2024-01-01'
    end = '2024-03-01'
    salary = 75000.0
    
    df = generate_transactions(start_date=start, end_date=end, monthly_salary=salary, num_random_transactions=800)
    
    output_path = 'data/data1.csv'
    df.to_csv(output_path, index=False)
    print(f"✅ Success! Generated {len(df)} transactions.")
    print(f"📅 Range: {start} to {end}")
    print(f"💰 Salary: ₹{salary}")
    print(f"📂 Saved to: {output_path}")
