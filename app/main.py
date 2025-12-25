from fastapi import FastAPI, Request
from .api.routes import router
from .etl import init_db, start_background_etl
from .config import settings
from .db import engine, Base  # <--- Added to access DB metadata

app = FastAPI(title="Kasparro Backend Assessment")

# --- DATABASE SCHEMA FIX ---
# Keep the line below uncommented for ONE deploy. 
# Once the app is running and the error is gone, comment it out and push again.
Base.metadata.drop_all(bind=engine) 
# ---------------------------

app.include_router(router)

SOURCES = [
    {"type": "api", "name": "jsonposts", "url": "https://jsonplaceholder.typicode.com/posts"},
    {"type": "csv", "name": "local_csv", "path": "./data/sample.csv"},
    {
        "type": "api", 
        "name": "coingecko", 
        "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    },
    {
        "type": "api", 
        "name": "coinpaprika", 
        "url": "https://api.coinpaprika.com/v1/tickers"
    }
]

@app.get("/")
@app.head("/") # Fixes the 405 Method Not Allowed error from Render's health checker
async def root():
    return {"status": "online", "message": "Kasparro API is running"}

@app.on_event("startup")
async def startup_event():
    init_db()
    start_background_etl(app, SOURCES)

@app.middleware("http")
async def add_request_meta(request: Request, call_next):
    response = await call_next(request)
    meta = getattr(request.state, "meta", {})
    if meta:
        response.headers["X-Request-ID"] = meta.get("request_id", "")
        response.headers["X-API-Latency-Ms"] = str(meta.get("api_latency_ms", 0))
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)