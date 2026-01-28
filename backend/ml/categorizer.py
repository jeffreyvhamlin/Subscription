from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np
import pickle
import os

class TransactionCategorizer:
    """
    NLP-based transaction categorization using TF-IDF + Logistic Regression
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=1000)
        self.categories = [
            'Streaming',      # Netflix, Spotify, Prime
            'Gym',            # Gym memberships
            'Utilities',      # Electricity, Water, Internet
            'Food',           # Groceries, Restaurants
            'EMI',            # Loan payments
            'Shopping',       # Online/offline shopping
            'Other'           # Miscellaneous
        ]
        self.is_trained = False
    
    def train(self, descriptions, labels):
        """
        Train the categorization model
        
        Args:
            descriptions: List of transaction descriptions
            labels: List of category labels
        """
        X = self.vectorizer.fit_transform(descriptions)
        self.model.fit(X, labels)
        self.is_trained = True
    
    def predict(self, description):
        """
        Predict category for a transaction description
        
        Args:
            description: Transaction description string
            
        Returns:
            Predicted category
        """
        if not self.is_trained:
            # Use rule-based categorization if not trained
            return self._rule_based_categorization(description)
        
        X = self.vectorizer.transform([description])
        return self.model.predict(X)[0]
    
    def _rule_based_categorization(self, description):
        """
        Simple rule-based categorization when ML model is not trained
        """
        description_upper = description.upper()
        
        # Streaming services
        streaming_keywords = ['NETFLIX', 'SPOTIFY', 'PRIME', 'AMAZON PRIME', 'DISNEY', 
                             'HBO', 'APPLE MUSIC', 'YOUTUBE PREMIUM']
        if any(kw in description_upper for kw in streaming_keywords):
            return 'Streaming'
        
        # Gym
        gym_keywords = ['GYM', 'FITNESS', 'PLANET', 'GOLD', 'CROSSFIT', 'YOGA']
        if any(kw in description_upper for kw in gym_keywords):
            return 'Gym'
        
        # Utilities
        utility_keywords = ['ELECTRICITY', 'WATER', 'GAS', 'INTERNET', 'MOBILE', 
                           'PHONE', 'BROADBAND', 'WIFI']
        if any(kw in description_upper for kw in utility_keywords):
            return 'Utilities'
        
        # Food
        food_keywords = ['RESTAURANT', 'CAFE', 'FOOD', 'GROCERY', 'SWIGGY', 
                        'ZOMATO', 'UBER EATS', 'DOMINO', 'PIZZA']
        if any(kw in description_upper for kw in food_keywords):
            return 'Food'
        
        # EMI
        emi_keywords = ['EMI', 'LOAN', 'CREDIT CARD', 'INSTALLMENT', 'FINANCE']
        if any(kw in description_upper for kw in emi_keywords):
            return 'EMI'
        
        # Shopping
        shopping_keywords = ['AMAZON', 'FLIPKART', 'MYNTRA', 'MALL', 'STORE', 'SHOP']
        if any(kw in description_upper for kw in shopping_keywords):
            return 'Shopping'
        
        return 'Other'
    
    def save_model(self, filepath='categorizer_model.pkl'):
        """Save trained model to file"""
        if self.is_trained:
            with open(filepath, 'wb') as f:
                pickle.dump({'vectorizer': self.vectorizer, 'model': self.model}, f)
    
    def load_model(self, filepath='categorizer_model.pkl'):
        """Load trained model from file"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.vectorizer = data['vectorizer']
                self.model = data['model']
                self.is_trained = True

def categorize_transactions(db, user_id):
    """
    Categorize all user transactions
    """
    from app.models import Transaction
    
    categorizer = TransactionCategorizer()
    
    # Get all uncategorized transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category.is_(None)
    ).all()
    
    for trans in transactions:
        category = categorizer.predict(trans.description)
        trans.category = category
    
    db.commit()
