from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, func
from .db import Base

class RawData(Base):
    """
    Stores the original, untouched payload from every source.
    Essential for the 'Auditability' requirement.
    """
    __tablename__ = "raw_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False)
    data = Column(JSON, nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

class Item(Base):
    """
    The Unified/Canonical table. 
    Instead of 'source' and 'external_id' being the unique key, 
    we use 'canonical_id' to merge duplicates across sources.
    """
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # CRITICAL FIX: The deterministic identity (e.g., a slug of the title)
    # This ensures "Source A" and "Source B" merge into one row.
    canonical_id = Column(String(255), unique=True, nullable=False) 
    
    title = Column(String(512))
    content = Column(Text)
    
    # MODULE 2 REQUIREMENT: Track which sources contributed to this record
    # Example: ["jsonposts", "local_csv"]
    contributing_sources = Column(JSON, default=list) 
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

class Checkpoint(Base):
    """
    Maintains the state of the ETL pipeline for incremental loading.
    """
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False, unique=True)
    last_run_at = Column(DateTime(timezone=True))
    last_status = Column(String(32))  # e.g., "success" or "failure"
    meta = Column(JSON)