from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
import os

# 1. Get the base URL
db_url = settings.DATABASE_URL or "sqlite:///./data/dev.db"

connect_args = {}

if db_url.startswith("sqlite"):
    os.makedirs("./data", exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    # 2. Standardize prefix for Psycopg 3
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    # 3. Handle SSL via Query Parameter (Most stable for Psycopg 3)
    if "sslmode" not in db_url:
        if "?" in db_url:
            db_url += "&sslmode=require"
        else:
            db_url += "?sslmode=require"

# 4. Create engine with no complex connect_args (let the URL do the work)
engine = create_engine(
    db_url, 
    connect_args=connect_args, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()