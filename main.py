from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from engine import analyze

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/signal/{ticker}")
def signal(ticker: str):
    try:
        return analyze(ticker.upper())
    except Exception as e:
        raise HTTPException(400, str(e))