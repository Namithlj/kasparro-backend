from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from urllib.parse import urlparse
import os

# SAFETY FALLBACK: Use local sqlite if environment variable is missing
db_url = settings.DATABASE_URL or "sqlite:///./data/dev.db"

if db_url.startswith("sqlite"):
    os.makedirs("./data", exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    # 1. FIX: Convert postgres:// to postgresql+psycopg://
    # This forces SQLAlchemy to use the v3 driver we installed
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    connect_args = {}
    parsed = urlparse(db_url)
    hostname = parsed.hostname or ""
    
    # Render and many cloud providers require SSL
    if hostname.endswith(".render.com") or "amazonaws.com" in hostname:
        connect_args["sslmode"] = "require"

# Enable pool_pre_ping to avoid stale/closed connections
engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()