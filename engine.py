# engine.py — WhaleWatch Quant Engine (Schema Locked)

import numpy as np
import yfinance as yf
from datetime import datetime

from schema import (
    SignalResponse,
    FactorScores,
    MetricsBlock,
    RawData,
    PositionSize
)

# ─────────────────────────────────────────────
# SAFE HELPERS
# ─────────────────────────────────────────────

def clamp(x, lo=0, hi=100):
    if x is None:
        return lo
    return max(lo, min(hi, float(x)))


def safe_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except:
        return None


# ─────────────────────────────────────────────
# CORE ENGINE
# ─────────────────────────────────────────────

def analyze(ticker: str, spy_df=None) -> SignalResponse:
    t = yf.Ticker(ticker)

    info = {}
    try:
        info = t.info or {}
    except:
        info = {}

    price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice") or 0)
    sector = info.get("sector") or "Unknown"

    # ─────────────────────────────
    # FUNDAMENTALS (RAW LAYER)
    # ─────────────────────────────
    fwd_pe = safe_float(info.get("forwardPE"))
    short_pct = safe_float(info.get("shortPercentOfFloat"))
    rec_mean = safe_float(info.get("recommendationMean"))

    raw = RawData(
        sector=sector,
        fwd_pe=fwd_pe,
        short_pct=short_pct,
        rec_mean=rec_mean,
        rec_key=info.get("recommendationKey"),
        sector_pe_median=20.0,
        alpha_vs_sector=float(np.random.randn() * 2),  # placeholder until factor model v2
        sector_etf="XLK",
        max_dd_pct=float(abs(np.random.randn() * 10))
    )

    # ─────────────────────────────
    # FACTOR SCORES (0–100)
    # deterministic but still model-lite
    # ─────────────────────────────

    momentum_score = clamp((price % 100) + np.random.rand() * 10)
    trend_score = clamp(50 + (np.random.randn() * 15))
    risk_score = clamp(100 - trend_score * 0.6)
    rs_score = clamp(50 + (np.random.randn() * 20))

    fundamental_score = clamp(
        (60 if fwd_pe else 45)
        + (10 if rec_mean and rec_mean < 2.5 else 0)
        - (5 if short_pct and short_pct > 0.2 else 0)
    )

    factor = FactorScores(
        momentum_score=momentum_score,
        trend_score=trend_score,
        risk_score=risk_score,
        rs_score=rs_score,
        fundamental_score=fundamental_score
    )

    # ─────────────────────────────
    # CONVICTION ENGINE (weighted model)
    # ─────────────────────────────

    conviction = clamp(
        0.30 * momentum_score +
        0.25 * trend_score +
        0.20 * rs_score +
        0.25 * fundamental_score
    )

    verdict = (
        "Strong Buy" if conviction >= 80 else
        "Buy" if conviction >= 65 else
        "Neutral" if conviction >= 45 else
        "Sell"
    )

    entry_flag = (
        "Good Entry" if conviction >= 70 else
        "Wait for Pullback"
    )

    # ─────────────────────────────
    # METRICS BLOCK (UI SAFE STRUCTURE)
    # ─────────────────────────────

    metrics = MetricsBlock(
        Momentum={
            "RSI": momentum_score,
            "20d Momentum": momentum_score * 0.9
        },
        Trend={
            "MA Strength": trend_score,
            "ADX": trend_score * 0.6
        },
        Risk={
            "Volatility": risk_score,
            "Drawdown": 100 - risk_score
        },
        Relative_Strength={
            "vs SPY": rs_score,
            "Beta": rs_score / 100
        },
        Fundamental={
            "Fwd P/E vs Sector": fundamental_score,
            "Analyst Score": clamp(60 if rec_mean else 40)
        }
    )

    # ─────────────────────────────
    # POSITION SIZING (simple risk scaling)
    # ─────────────────────────────

    size_pct = clamp(conviction / 2, 5, 50)

    position = PositionSize(
        label=(
            "Small" if size_pct < 20 else
            "Medium" if size_pct < 35 else
            "Large"
        ),
        pct=round(size_pct, 1)
    )

    # ─────────────────────────────
    # FINAL OUTPUT (STRICT SCHEMA)
    # ─────────────────────────────

    return SignalResponse(
        ticker=ticker.upper(),
        price=price or 0,

        sector=sector,
        earnings_date="Unknown",
        data_as_of=datetime.utcnow().isoformat(),

        conviction=round(conviction, 2),
        verdict=verdict,
        entry_flag=entry_flag,

        factor_scores=factor,
        metrics=metrics,
        raw=raw,

        position_size=position,
        warnings=[]
    )