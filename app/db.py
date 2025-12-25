from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from urllib.parse import urlparse


# Configure DBAPI connection args and engine options
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
else:
    # Default connect args for psycopg2; apply SSL when connecting to Render external hosts
    connect_args = {}
    parsed = urlparse(settings.DATABASE_URL)
    hostname = parsed.hostname or ""
    if hostname.endswith(".render.com"):
        connect_args["sslmode"] = "require"

    # Enable pool_pre_ping to avoid stale/closed connections
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
