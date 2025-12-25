import asyncio
from .db import engine, Base, SessionLocal
from .services.ingestion import run_etl
from .config import settings
from datetime import datetime


def init_db():
    Base.metadata.create_all(bind=engine)


async def etl_loop(sources):
    while True:
        db = SessionLocal()
        try:
            run_etl(db, sources, settings.API_KEY)
        finally:
            db.close()
        await asyncio.sleep(settings.ETL_INTERVAL_SECONDS)


def start_background_etl(app, sources):
    loop = asyncio.get_event_loop()
    loop.create_task(etl_loop(sources))
