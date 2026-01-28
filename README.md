# 💰 Smart Subscription & Bill Guardian

An intelligent financial application that automatically detects subscriptions, EMIs, and recurring bills from bank transactions, predicts cash flow issues, and provides plain-language alerts.

## 🌟 Features

- **🔍 Automatic Subscription Detection**: Uses ML-based periodicity mining to detect recurring payments
- **📊 Balance Forecasting**: Predicts your balance for the next 30 days
- **⚠️ Smart Alerts**: Plain-language notifications like *"Your Spotify + Prime + Gym will cost ₹4,320 this month. Cancelling Gym saves ₹1,200. Risk of low balance on 26th."*
- **📈 Beautiful Dashboard**: Modern UI with D3.js visualizations
- **🏷️ NLP Categorization**: Automatically categorizes transactions using machine learning
- **🔐 Secure**: JWT authentication, password hashing, and data encryption

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend API** | FastAPI | REST endpoints for auth, uploads, analysis |
| **Database** | SQLite + SQLAlchemy | Store users and transactions |
| **Data Processing** | Pandas, scikit-learn | Cleaning, pattern mining, ML |
| **ML/NLP** | scikit-learn | Categorization, forecasting |
| **Scheduling** | APScheduler | Background jobs for detection |
| **Frontend** | HTML/CSS/JS + D3.js | Dashboard visualizations |
| **Security** | JWT, bcrypt, AES-256 | Authentication & encryption |

## 📁 Project Structure

```
Subscription_Project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT authentication
│   │   ├── database.py          # Database connection
│   │   └── routers/             # API endpoints
│   ├── ml/
│   │   ├── periodicity_detector.py  # Recurring pattern detection
│   │   ├── categorizer.py           # NLP categorization
│   │   ├── forecaster.py            # Balance forecasting
│   ├── services/
│   │   ├── transaction_processor.py # CSV parsing
│   │   ├── notification_service.py  # Alert generation
│   │   └── scheduler.py             # Background jobs
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Main dashboard
│   ├── login.html               # Authentication
│   └── js/                      # JavaScript logic
└── data/
    └── sample_transactions.csv  # Sample data
```

## 🚀 Quick Start

### 1. Set up Python Environment

```bash
# Navigate to project directory
cd "e:\TCD MSc DS\Projects\Subscription_Project"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Start the Backend

```bash
# From the project root directory
cd backend
..\venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`
- API Documentation: `http://127.0.0.1:8000/docs`

### 3. Open the Frontend

Using a local server (recommended):

```bash
cd frontend
python -m http.server 8081
```

Then visit `http://127.0.0.1:8081/login.html`

## 📝 Usage

### 1. Register/Login
- Open the frontend and create an account
- Login with your credentials

### 2. Upload Bank Transactions
- Use the sample CSV file: `data/sample_transactions.csv`
- Or upload your own CSV in this format:
  ```csv
  Date,Description,Debit,Credit
  2024-01-05,NETFLIX.COM SUBSCRIPTION,199,
  2024-01-10,SALARY CREDIT,,50000
  ```

### 3. View Insights
- **Dashboard**: See total transactions, subscriptions, and monthly costs
- **Balance Forecast**: 30-day prediction chart
- **Subscriptions**: Detected recurring payments
- **Notifications**: Smart alerts and savings opportunities

## 🔬 How It Works

### Periodicity Detection Algorithm
1. Groups similar transactions using fuzzy string matching
2. Calculates time intervals between transactions
3. Detects monthly (25-35 days), weekly (6-8 days), or quarterly (85-95 days) patterns
4. Provides confidence score based on consistency

### NLP Categorization
- Uses TF-IDF + Logistic Regression for baseline
- Categories: Streaming, Gym, Utilities, Food, EMI, Shopping, Other
- Falls back to rule-based categorization if ML model not trained

### Balance Forecasting
- Analyzes historical transaction patterns
- Projects future balance considering upcoming subscriptions
- Identifies low balance risk dates

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configured for production
- **Input Validation**: Pydantic schemas for all endpoints

## 📊 Sample Data

The included `sample_transactions.csv` contains:
- Monthly subscriptions: Netflix (₹199), Spotify (₹149), Gym (₹1,200)
- Monthly EMI: Personal Loan (₹5,500)
- Monthly bills: Electricity (~₹1,800)
- Irregular transactions: Food, shopping, etc.

## 🎨 Frontend Features

- **Modern Dark Theme**: Glassmorphism effects with gradient backgrounds
- **Responsive Design**: Works on desktop and mobile
- **Interactive Charts**: D3.js balance forecast with tooltips
- **Drag & Drop Upload**: Easy CSV file handling
- **Real-time Notifications**: Bell icon with unread count

## 🔮 Future Enhancements

- [ ] Upgrade to BERT for better NLP categorization
- [ ] Email/SMS notifications via SendGrid/Twilio
- [ ] Subscription cancellation tracking
- [ ] Budget recommendations
- [ ] Mobile app (React Native)
- [ ] Multi-bank account support

## 📄 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Transactions
- `POST /api/transactions/upload` - Upload CSV
- `GET /api/transactions` - List transactions
- `GET /api/transactions/stats` - Get statistics
- `GET /api/transactions/forecast` - Balance forecast

### Subscriptions
- `GET /api/subscriptions` - List subscriptions
- `GET /api/subscriptions/upcoming` - Upcoming charges
- `PUT /api/subscriptions/{id}` - Update subscription
- `GET /api/subscriptions/notifications` - Get notifications

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure all dependencies are installed: `pip install -r backend/requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

**Frontend can't connect to backend:**
- Verify backend is running on `http://localhost:8000`
- Check CORS settings in `backend/app/main.py`

**CSV upload fails:**
- Ensure CSV has headers: `Date, Description, Debit, Credit` or `Date, Description, Amount`
- Check date format is parseable by pandas

## 👨‍💻 Development

Built with ❤️ using FastAPI, scikit-learn, and D3.js

Author: Jeffrey Hamlin  
Institution: Trinity College Dublin - MSc Data Science

## 📜 License

MIT License - feel free to use for personal or educational purposes
