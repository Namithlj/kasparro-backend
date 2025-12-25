from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from ..db import get_db
from ..models import Item, Checkpoint
from ..schemas import ItemOut, HealthResponse
from ..config import settings
import time
import uuid
from ..etl import run_etl as run_etl_now
from ..db import SessionLocal

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Kasparro Backend Assessment", "docs": "/docs", "health": "/health"}


@router.get("/data", response_model=list[ItemOut])
def get_data(request: Request, source: Optional[str] = None, page: int = 1, page_size: int = settings.DEFAULT_PAGE_SIZE, q: Optional[str] = None, db: Session = Depends(get_db)):
    start = time.time()
    query = db.query(Item)
    if source:
        query = query.filter(Item.source == source)
    if q:
        q_like = f"%{q}%"
        query = query.filter((Item.title.ilike(q_like)) | (Item.content.ilike(q_like)))
    offset = (page - 1) * page_size
    items = query.order_by(Item.id.desc()).offset(offset).limit(page_size).all()
    latency = int((time.time() - start) * 1000)
    request.state.meta = {"request_id": str(uuid.uuid4()), "api_latency_ms": latency}
    return items


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False
    cp = db.query(Checkpoint).order_by(Checkpoint.id.desc()).first()
    etl_meta = None
    if cp:
        etl_meta = {"source": cp.source, "last_status": cp.last_status, "last_run_at": cp.last_run_at}
    return {"db": db_ok, "etl_last_run": etl_meta}


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(Item).count()
    cp = db.query(Checkpoint).order_by(Checkpoint.id.desc()).first()
    return {"records_processed": total, "last_checkpoint": (cp.meta if cp else None)}

@router.post("/run-etl")
def run_etl_endpoint(x_api_key: Optional[str] = None, x_api_key_header: Optional[str] = Header(None, alias="x-api-key")):
    # accept API key from query (`x_api_key`) or header (`x-api-key`)
    effective_key = x_api_key_header or x_api_key
    if settings.API_KEY and effective_key != settings.API_KEY:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="unauthorized")
    db = SessionLocal()
    try:
        # run with the SOURCES defined in main; import here to avoid cycle
        from ..main import SOURCES

        res = run_etl_now(db, SOURCES, settings.API_KEY)
    finally:
        db.close()
    return res
