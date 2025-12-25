import os
from app.services.ingestion import normalize_api_record, normalize_csv_record, run_etl
from app.db import Base, engine, SessionLocal


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_normalize_api_record():
    r = {"id": 5, "title": "t", "body": "b"}
    n = normalize_api_record(r)
    assert n["external_id"] == "5"
    assert n["title"] == "t"


def test_normalize_csv_record(tmp_path, monkeypatch):
    p = tmp_path / "sample.csv"
    p.write_text("external_id,title,content\n10,hi,hello\n")
    sources = [{"type": "csv", "name": "testcsv", "path": str(p)}]
    db = SessionLocal()
    res = run_etl(db, sources)
    assert res["records_processed"] >= 1
