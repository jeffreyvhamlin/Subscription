from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Transaction Schemas
class TransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float
    category: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    is_recurring: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionResponse(BaseModel):
    id: int
    name: str
    amount: float
    frequency: str
    next_payment_date: Optional[datetime]
    last_payment_date: Optional[datetime]
    status: str
    confidence_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionUpdate(BaseModel):
    status: Optional[str] = None

# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    message: str
    type: str
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Statistics Schemas
class TransactionStats(BaseModel):
    total_transactions: int
    total_subscriptions: int
    monthly_subscription_cost: float
    total_spent_this_month: float
    avg_spent_per_month: float
    total_spent_overall: float
    
# Forecast Schemas
class BalanceForecast(BaseModel):
    dates: List[str]
    predicted_balance: List[float]
    low_balance_dates: List[str]
    
class UpcomingCharge(BaseModel):
    subscription_name: str
    amount: float
    date: datetime
