from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, func, UniqueConstraint
from .db import Base


class RawData(Base):
    __tablename__ = "raw_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False)
    data = Column(JSON, nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False)
    external_id = Column(String(128), nullable=False)
    title = Column(String(512))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint('source', 'external_id', name='uq_source_external'),)


class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False, unique=True)
    last_external_id = Column(String(128))
    last_run_at = Column(DateTime(timezone=True))
    last_status = Column(String(32))
    meta = Column(JSON)
