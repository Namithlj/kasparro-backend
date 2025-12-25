# Kasparro — Backend & ETL Systems (Starter Project)

Overview
========
This repository contains a minimal, runnable backend + ETL skeleton that satisfies the P0/P1 requirements of the Kasparro assignment. It includes:

- An ETL that ingests from one remote API and one CSV file
- Normalization and idempotent writes into Postgres
- Simple checkpointing
- FastAPI service exposing `/data`, `/health`, and `/stats`
- Dockerfile and `docker-compose.yml` for local runs
- `Makefile` targets: `make up`, `make down`, `make test`

Quick start (local, using Docker)
---------------------------------

1. Copy `.env.example` to `.env` and adjust values as needed.
2. Start services:

```bash
make up
```

3. The API will be available at `http://localhost:8000`.
  - Health: GET http://localhost:8000/health
  - Data: GET http://localhost:8000/data

Design Notes
------------
- Config values live in `app/config.py` and are configurable via environment variables.
- The app starts an ETL loop on FastAPI startup and runs every `ETL_INTERVAL_SECONDS`.
- Raw payloads are stored in `raw_data`; normalized rows are stored in `items`.
- Checkpoints are stored in `checkpoints` to support incremental logic.

Tests
-----
Run tests locally (without Docker):

```bash
pip install -r requirements.txt
make test
```

Next steps for integration
 Replace API URLs in `app/main.py` `SOURCES` with provided API endpoints and set `API_KEY` in `.env`.
 Add cloud deployment and scheduled runs (Render) for full evaluation.

Render deployment (free tier)
-----------------------------
1. Create an account at https://render.com and install the Render dashboard CLI if desired.
2. Create a new Web Service and connect your GitHub repo (or use the `render.yaml` manifest included).
  - Choose `Docker` environment and use the `Dockerfile` in this repo.
  - Set environment variables in Render: `DATABASE_URL`, `API_KEY` (optional), `ETL_INTERVAL_SECONDS`.
3. Add a Scheduled Job / Cron Job on Render (or use the `cronJobs` section in `render.yaml`):
  - Example command: `curl -X POST https://<your-service>.onrender.com/run-etl -H "x-api-key: $API_KEY"`
  - Schedule: every 15 minutes (or as required).
4. Verify the service at `https://<your-service>.onrender.com/health` and call `/run-etl` to trigger a manual run.

Notes
-----
- Render's free plan supports web services; managed Postgres may require a paid plan — you can use an external free Postgres provider or Render's managed DB if available in your account.
- Ensure secrets are stored in Render's dashboard (do not commit `.env` with real keys).
