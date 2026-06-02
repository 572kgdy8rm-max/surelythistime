# main.py — WhaleWatch API v2 (Schema Locked)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine import analyze

app = FastAPI(title="WhaleWatch v4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "alive"}

# ─────────────────────────────────────────────
# SINGLE TICKER SIGNAL
# ─────────────────────────────────────────────
@app.get("/signal/{ticker}")
def signal(ticker: str):
    return analyze(ticker)

# ─────────────────────────────────────────────
# SIMPLE SCAN (no basket complexity yet)
# ─────────────────────────────────────────────
@app.get("/scan")
def scan(tickers: str):
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t]

    results = []
    for t in ticker_list[:20]:
        try:
            results.append(analyze(t))
        except:
            continue

    results.sort(key=lambda x: x.conviction, reverse=True)

    return {
        "results": results,
        "count": len(results)
    }