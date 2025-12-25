from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from urllib.parse import urlparse
import os

# SAFETY FALLBACK: Use local sqlite if environment variable is missing
# This prevents the 'NoneType' has no attribute 'startswith' error
db_url = settings.DATABASE_URL or "sqlite:///./data/dev.db"

if db_url.startswith("sqlite"):
    # Create the data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}
    parsed = urlparse(db_url)
    hostname = parsed.hostname or ""
    # Render and many cloud providers require SSL for external connections
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