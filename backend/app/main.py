from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
from pathlib import Path

# Add backend directory to path to access sibling packages (services, ml, app)
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from .database import init_db
from .routers import auth, transactions, subscriptions

# Initialize FastAPI app
app = FastAPI(
    title="Smart Subscription & Bill Guardian",
    description="Automatically detect subscriptions and recurring bills, predict cash flow issues",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null"  # For file:// protocol
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(subscriptions.router)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Smart Subscription & Bill Guardian API",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
