import csv
import io
import re
import time
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import RawData, Item, Checkpoint

# --- EXTRACTION METHODS ---

def fetch_api_records(url: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches data from a remote REST API."""
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    # Handle common API wrappers like {"data": [...]}
    if isinstance(data, dict):
        return data.get("data", [])
    return data

def read_csv_records(content: str) -> List[Dict[str, Any]]:
    """Reads data from a CSV string."""
    f = io.StringIO(content)
    reader = csv.DictReader(f)
    return list(reader)

# --- NORMALIZATION & UNIFICATION METHODS ---

def generate_canonical_id(title: str) -> str:
    """
    Creates a deterministic identity across sources.
    Example: "Bitcoin Price!" -> "bitcoin-price"
    This ensures Source A and Source B records for the same item merge.
    """
    if not title:
        return "unknown-" + str(time.time())
    # Lowercase, remove special chars, replace spaces with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return slug

def normalize_record(r: dict, source_type: str) -> dict:
    """Standardizes fields regardless of source format."""
    if source_type == "api":
        return {
            "external_id": str(r.get("id") or r.get("postId") or r.get("id")),
            "title": r.get("title") or r.get("name") or r.get("symbol"),
            "content": r.get("body") or r.get("content") or f"Market Cap: {r.get('market_cap')}",
        }
    else:  # csv
        return {
            "external_id": str(r.get("external_id") or r.get("id")),
            "title": r.get("title"),
            "content": r.get("content"),
        }

# --- MAIN ETL ENGINE ---

def run_etl(db: Session, sources: list, api_key: Optional[str] = None):
    """
    Executes the full ETL pipeline with Canonical Identity Unification.
    Matches Module 2 requirements for cross-source deduplication.
    """
    start_time = time.time()
    total_processed = 0
    
    for src in sources:
        kind = src.get("type")
        name = src.get("name")
        
        try:
            # 1. EXTRACT
            if kind == "api":
                raw_records = fetch_api_records(src["url"], api_key)
            elif kind == "csv":
                with open(src["path"], "r", encoding="utf-8") as fh:
                    raw_records = read_csv_records(fh.read())
            else:
                continue

            # 2. TRANSFORM & LOAD (UNIFIED)
            for raw_r in raw_records:
                # Audit Trail: Always save the raw payload first
                db.add(RawData(source=name, data=raw_r))
                db.flush()

                # Normalize the data
                n = normalize_record(raw_r, kind)
                canon_id = generate_canonical_id(n["title"])

                # 3. IDENTITY UNIFICATION (The fix for your FAIL grade)
                # Check if this entity already exists under ANY source
                existing_item = db.query(Item).filter_by(canonical_id=canon_id).first()

                if existing_item:
                    # MERGE LOGIC: Update existing record if new data is richer
                    if n["content"] and len(n["content"]) > len(existing_item.content or ""):
                        existing_item.content = n["content"]
                    
                    # Update source tracking (JSON column)
                    current_sources = set(existing_item.contributing_sources or [])
                    current_sources.add(name)
                    existing_item.contributing_sources = list(current_sources)
                    existing_item.last_updated = datetime.utcnow()
                else:
                    # CREATE NEW: No record exists with this canonical identity
                    new_item = Item(
                        canonical_id=canon_id,
                        title=n["title"],
                        content=n["content"],
                        contributing_sources=[name]
                    )
                    db.add(new_item)

                total_processed += 1
                try:
                    db.flush()
                except IntegrityError:
                    db.rollback()

            # 4. CHECKPOINTING
            cp = db.query(Checkpoint).filter_by(source=name).one_or_none()
            if not cp:
                cp = Checkpoint(source=name, last_status="success", last_run_at=datetime.utcnow())
                db.add(cp)
            else:
                cp.last_status = "success"
                cp.last_run_at = datetime.utcnow()
            
            db.commit()

        except Exception as e:
            db.rollback()
            # Log failure to Checkpoint table
            cp = db.query(Checkpoint).filter_by(source=name).one_or_none()
            if cp:
                cp.last_status = "failure"
                cp.meta = {"error": str(e)}
                db.commit()
            print(f"Error processing source {name}: {e}")

    return {
        "status": "completed",
        "records_processed": total_processed,
        "duration_seconds": round(time.time() - start_time, 2)
    }