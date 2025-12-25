from fastapi import FastAPI, Request
from .api.routes import router
from .etl import init_db, start_background_etl
from .config import settings

app = FastAPI(title="Kasparro Backend Assessment")
app.include_router(router)

SOURCES = [
    {"type": "api", "name": "jsonposts", "url": "https://jsonplaceholder.typicode.com/posts"},
    {"type": "csv", "name": "local_csv", "path": "./data/sample.csv"},
    {"type": "api", "name": "coingecko_markets", "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"},
]


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
