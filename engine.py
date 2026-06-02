import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

from metadata import get_metadata
from options import compute_options_overlay


def clamp(x, a=0, b=100):
    return max(a, min(b, x))


def analyze(ticker: str, spy_df=None):

    t = yf.Ticker(ticker)
    hist = t.history(period="6mo")

    if hist.empty:
        raise ValueError("No data")

    price = float(hist["Close"].iloc[-1])

    # ───────────────────────────────
    # METADATA
    # ───────────────────────────────
    meta = get_metadata(ticker)

    # ───────────────────────────────
    # MOMENTUM
    # ───────────────────────────────
    returns = hist["Close"].pct_change().dropna()
    mom_20d = returns.tail(20).sum() * 100

    momentum_score = clamp(50 + mom_20d * 5)

    # ───────────────────────────────
    # TREND
    # ───────────────────────────────
    ma50 = hist["Close"].rolling(50).mean().iloc[-1]
    ma200 = hist["Close"].rolling(200).mean().iloc[-1]

    trend_score = 50
    if price > ma50: trend_score += 20
    if price > ma200: trend_score += 30

    trend_score = clamp(trend_score)

    # ───────────────────────────────
    # RISK
    # ───────────────────────────────
    vol = returns.std() * np.sqrt(252)
    risk_score = clamp(100 - vol * 100)

    # ───────────────────────────────
    # RELATIVE STRENGTH (vs SPY optional)
    # ───────────────────────────────
    rs_score = 60  # placeholder stable baseline

    # ───────────────────────────────
    # FUNDAMENTAL
    # ───────────────────────────────
    fwd_pe = meta["fwd_pe"] or 0
    fund_score = clamp(70 - (fwd_pe / 10 if fwd_pe else 0))

    # ───────────────────────────────
    # OPTIONS OVERLAY
    # ───────────────────────────────
    opt = compute_options_overlay(
        ticker,
        price,
        meta["earnings_date"],
        volatility=vol
    )

    # ───────────────────────────────
    # CONVICTION MODEL
    # ───────────────────────────────
    conviction = (
        momentum_score * 0.25 +
        trend_score * 0.30 +
        risk_score * 0.15 +
        rs_score * 0.10 +
        fund_score * 0.20
    )

    conviction += opt["conviction_adjustment"]

    conviction = clamp(conviction)

    # ───────────────────────────────
    # VERDICT
    # ───────────────────────────────
    if conviction >= 80:
        verdict = "Strong Buy"
    elif conviction >= 65:
        verdict = "Buy"
    elif conviction >= 45:
        verdict = "Neutral"
    else:
        verdict = "Sell"

    entry_flag = "Good Entry" if momentum_score > 60 else "Wait for Pullback"

    return {
        "ticker": ticker,
        "price": price,
        "sector": meta["sector"],
        "earnings_date": meta["earnings_date"],

        "conviction": round(conviction, 1),
        "verdict": verdict,
        "entry_flag": entry_flag,
        "position_size": {"label": "medium", "pct": 5},

        "metrics": {
            "Momentum": {
                "20d Momentum": round(mom_20d, 2)
            },
            "Trend": {
                "Price vs MA50": float(price - ma50),
                "Price vs MA200": float(price - ma200)
            },
            "Risk": {
                "Volatility": float(vol)
            },
            "Relative Strength": {},
            "Fundamental": {
                "Fwd P/E vs Sector": fwd_pe
            }
        },

        "scores": {
            "momentum_score": round(momentum_score, 1),
            "trend_score": round(trend_score, 1),
            "risk_score": round(risk_score, 1),
            "rs_score": rs_score,
            "fundamental_score": fund_score
        },

        "raw": {
            **meta,
            "ma50": ma50,
            "ma200": ma200,
            "vol": vol
        },

        "options": opt,
        "warnings": [],
        "data_as_of": datetime.utcnow().isoformat()
    }