import csv
import io
import time
import requests
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional
from ..models import RawData, Item, Checkpoint


def fetch_api_records(url: str, api_key: Optional[str] = None):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def read_csv_records(content: str):
    f = io.StringIO(content)
    reader = csv.DictReader(f)
    return list(reader)


def normalize_api_record(r: dict):
    return {
        "external_id": str(r.get("id") or r.get("postId") or r.get("external_id")),
        "title": r.get("title") or r.get("name"),
        "content": r.get("body") or r.get("content"),
        "created_at": None,
    }


def normalize_csv_record(r: dict):
    return {
        "external_id": str(r.get("external_id") or r.get("id")),
        "title": r.get("title"),
        "content": r.get("content"),
        "created_at": None,
    }


def run_etl(db, sources: list, api_key: Optional[str] = None):
    start = time.time()
    total = 0
    last_success = None
    last_failure = None
    for src in sources:
        kind = src.get("type")
        name = src.get("name")
        try:
            if kind == "api":
                records = fetch_api_records(src["url"], api_key)
                if isinstance(records, dict):
                    records = records.get("data", [])
                norm = [normalize_api_record(r) for r in records]
            elif kind == "csv":
                with open(src["path"], "r", encoding="utf-8") as fh:
                    content = fh.read()
                csv_rows = read_csv_records(content)
                norm = [normalize_csv_record(r) for r in csv_rows]
            else:
                norm = []

            for raw_r, n in zip(records if kind == "api" else csv_rows, norm):
                rd = RawData(source=name, data=raw_r)
                db.add(rd)
            db.flush()

            for n in norm:
                total += 1
                item = Item(
                    source=name,
                    external_id=n["external_id"],
                    title=n.get("title"),
                    content=n.get("content"),
                )
                db.add(item)
                try:
                    db.flush()
                except IntegrityError:
                    db.rollback()
            cp = db.query(Checkpoint).filter_by(source=name).one_or_none()
            if not cp:
                cp = Checkpoint(source=name, last_status="success")
                db.add(cp)
            else:
                cp.last_status = "success"
            db.commit()
            last_success = datetime.utcnow()
        except Exception as e:
            db.rollback()
            cp = db.query(Checkpoint).filter_by(source=name).one_or_none()
            if not cp:
                cp = Checkpoint(source=name, last_status="failure")
                db.add(cp)
            else:
                cp.last_status = "failure"
            cp.meta = {"error": str(e)}
            db.commit()
            last_failure = datetime.utcnow()

    duration = time.time() - start
    return {"records_processed": total, "duration_seconds": duration, "last_success": last_success, "last_failure": last_failure}
