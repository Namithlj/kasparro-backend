#!/usr/bin/env python3
"""Simple management script to init DB and run ETL using repo code.

Usage:
  # initialize DB schema (reads DATABASE_URL from env)
  python scripts/manage_db.py init-db

  # run ETL once (reads DATABASE_URL and API_KEY from env)
  python scripts/manage_db.py run-etl
"""
import sys
import os
from pprint import pprint

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    # ensure env hints
    print("DATABASE_URL:", os.environ.get("DATABASE_URL"))
    print("API_KEY:", "(set)" if os.environ.get("API_KEY") else "(not set)")

    if cmd == "init-db":
        # create tables
        from app.etl import init_db

        init_db()
        print("Database initialized (tables created where possible).")

    elif cmd == "run-etl":
        # run ETL once
        from app.db import SessionLocal
        from app.etl import run_etl as run_etl_now
        # import SOURCES from main to reuse same sources
        from app.main import SOURCES
        from app.config import settings

        db = SessionLocal()
        try:
            res = run_etl_now(db, SOURCES, settings.API_KEY)
            pprint(res)
        finally:
            db.close()

    else:
        print(__doc__)
        sys.exit(1)
