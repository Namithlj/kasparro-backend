from pydantic import BaseModel
from typing import Any, Optional, Dict
from datetime import datetime


class ItemOut(BaseModel):
    id: int
    source: str
    external_id: str
    title: Optional[str]
    content: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class HealthResponse(BaseModel):
    db: bool
    etl_last_run: Optional[Dict[str, Any]] = None


class StatsResponse(BaseModel):
    records_processed: int
    duration_seconds: float
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
