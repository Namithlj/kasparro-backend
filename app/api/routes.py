from fastapi import APIRouter, Depends, Request, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import time
import uuid

from ..db import get_db, SessionLocal
from ..models import Item, Checkpoint
from ..schemas import ItemOut, HealthResponse
from ..config import settings
from ..services.ingestion import run_etl as run_etl_now

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Kasparro Unified Backend", "docs": "/docs", "health": "/health"}

@router.get("/data", response_model=List[ItemOut])
def get_data(
    request: Request, 
    source: Optional[str] = None, 
    page: int = 1, 
    page_size: int = settings.DEFAULT_PAGE_SIZE, 
    q: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    start = time.time()
    query = db.query(Item)
    
    # NEW LOGIC: Filter within the JSON list of contributing sources
    if source:
        # This checks if 'source' exists inside the JSON array
        query = query.filter(Item.contributing_sources.contains([source]))
    
    # Global Search logic remains similar but queries the Unified table
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
        etl_meta = {
            "source": cp.source, 
            "last_status": cp.last_status, 
            "last_run_at": cp.last_run_at
        }
    return {"db": db_ok, "etl_last_run": etl_meta}

@router.post("/run-etl")
def run_etl_endpoint(
    x_api_key: Optional[str] = Header(None, alias="x-api-key"),
    db: Session = Depends(get_db)
):
    # Security check using the settings API key
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="unauthorized")
    
    # Import SOURCES from main to avoid circular imports
    from ..main import SOURCES
    
    res = run_etl_now(db, SOURCES, settings.API_KEY)
    return res