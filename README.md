# Kasparro — Backend & ETL Systems (Starter Project)

Overview
========
This repository contains a minimal, runnable backend + ETL system designed to satisfy the **P0 / P1 requirements** of the Kasparro Backend & ETL assignment.

The project demonstrates how to:
- Ingest data from multiple heterogeneous sources
- Normalize and persist data reliably
- Design idempotent ETL pipelines
- Expose clean, production-style APIs
- Run locally and deploy easily using Docker and Render

This is intentionally **not an over-engineered system**. The focus is on **correctness, clarity, extensibility, and system thinking**, rather than feature bloat.

---

What This Project Includes
==========================
- An ETL pipeline that ingests data from:
  - One remote API
  - One local CSV file
- Data normalization and idempotent writes into Postgres
- Simple checkpointing to support incremental ingestion
- A FastAPI backend exposing:
  - `/health`
  - `/data`
  - `/stats`
  - `/run-etl`
- Dockerfile and `docker-compose.yml` for local execution
- Makefile for common developer workflows
- Render-ready deployment setup

---

Live Deployment
===============
The backend is deployed on Render (free tier).

Base URL:
https://kasparrobackend.onrender.com/docs


Swagger / API Docs:
https://kasparrobackend.onrender.com/docs




---

High-Level Architecture
=======================

┌───────────────┐
│ Remote API │
└───────┬───────┘
│
┌───────▼───────┐
│ │
│ ETL │
│ (Extract → │
│ Transform → │
│ Load) │
│ │
└───────┬───────┘
│
┌───────▼───────┐
│ Postgres │
│ │
│ raw_data │
│ items │
│ checkpoints │
│ │
└───────┬───────┘
│
┌───────▼───────┐
│ FastAPI │
│ │
│ /health │
│ /data │
│ /stats │
│ /run-etl │
└───────────────┘


2. Environment setup

Copy the example environment file:

cp .env.example .env


Edit .env and set values as needed:

DATABASE_URL

API_KEY

ETL_INTERVAL_SECONDS

3. Start services
make up


This will:

Start Postgres

Build the backend image

Start the FastAPI service

Automatically start the ETL loop

4. Access the API
http://localhost:8000


Available endpoints:

Health: GET /health

Data: GET /data

Stats: GET /stats

Docs: GET /docs

ETL Design

The ETL pipeline follows a clear and predictable flow:

Extract

Fetches data from:

A remote HTTP API

A CSV file on disk

Transform

Normalizes incoming data into a consistent internal schema

Handles missing or malformed fields safely

Prepares records for idempotent insertion

Load

Raw payloads are stored in the raw_data table

Normalized records are stored in the items table

Writes are idempotent (safe to re-run)

Checkpointing & Idempotency

To support incremental ingestion:

Each source maintains a checkpoint

Checkpoints are stored in the checkpoints table

ETL resumes from the last successful position

Duplicate processing is avoided

This ensures:

Safe retries

No duplicate rows

Predictable ETL behavior

Database Tables
raw_data

Stores unmodified source payloads for traceability and debugging.

items

Stores normalized, query-ready records exposed via the API.

checkpoints

Stores ETL progress metadata per source.

API Endpoints
Health Check

Used for monitoring and deployment health checks.

GET /health


Response:

{ "status": "ok" }

Fetch Data

Returns normalized records from the database.

GET /data


Optional query parameters:

limit

offset

ETL Stats

Provides visibility into ETL execution state.

GET /stats


Example response:

{
  "last_run": "2025-12-25T10:40:00Z",
  "rows_ingested": 1200
}

Trigger ETL Manually

Allows manual or scheduled triggering (used by Render Cron).

POST /run-etl


Headers:

x-api-key: YOUR_API_KEY

Tests

Run tests locally (without Docker):

pip install -r requirements.txt
make test

Render Deployment (Free Tier)

Create an account at https://render.com

Create a new Web Service

Connect this GitHub repository

Choose Docker as the environment

Set environment variables in Render:

DATABASE_URL

API_KEY

ETL_INTERVAL_SECONDS

Deploy the service

Optional: Add a Render Cron Job to trigger ETL runs:

curl -X POST https://kasparrobackend.onrender.com/run-etl \
  -H "x-api-key: $API_KEY"

Design Tradeoffs & Assumptions

Focused on correctness and clarity over feature breadth

Minimal schema to keep ETL logic understandable

No authentication layer beyond API key (out of scope)

ETL logic kept synchronous for simplicity

Next Steps

Replace placeholder source APIs with production endpoints

Add authentication & rate limiting

Improve observability (logging, metrics)

Integrate with frontend dashboards

Add CI/CD pipelines

Notes

Do not commit .env files with real secrets

Render free tier may require external Postgres

This project is intentionally scoped to demonstrate engineering fundamentals


