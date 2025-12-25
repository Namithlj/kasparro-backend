from pydantic import BaseModel
from typing import Any, Optional, Dict, List
from datetime import datetime

class ItemOut(BaseModel):
    """
    Schema for the Unified/Canonical record.
    Reflects the deduplicated entity rather than a source-specific row.
    """
    id: int
    canonical_id: str  # The unique identity fingerprint (e.g., 'bitcoin-price')
    title: Optional[str]
    content: Optional[str]
    
    # Shows which sources were merged to create this item
    contributing_sources: List[str] 
    
    created_at: Optional[datetime]
    last_updated: Optional[datetime]

    class Config:
        orm_mode = True


class HealthResponse(BaseModel):
    """Monitoring schema for deployment readiness."""
    db: bool
    etl_last_run: Optional[Dict[str, Any]] = None


class StatsResponse(BaseModel):
    """Schema for visibility into ETL performance."""
    records_processed: int
    duration_seconds: float
    last_success: Optional[datetime]
    last_failure: Optional[datetime]