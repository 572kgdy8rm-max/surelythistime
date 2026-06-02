# schema.py — WhaleWatch Locked Contract

from pydantic import BaseModel
from typing import Dict, Optional, List


# ─────────────────────────────────────────────
# RAW FUNDAMENTALS (yfinance / external data)
# ─────────────────────────────────────────────
class RawData(BaseModel):
    sector: str = "Unknown"
    fwd_pe: Optional[float] = None
    short_pct: Optional[float] = None
    rec_mean: Optional[float] = None
    rec_key: Optional[str] = None

    sector_pe_median: Optional[float] = None
    alpha_vs_sector: Optional[float] = None
    sector_etf: Optional[str] = None

    max_dd_pct: Optional[float] = None


# ─────────────────────────────────────────────
# CORE FACTOR SCORES (0–100)
# ─────────────────────────────────────────────
class FactorScores(BaseModel):
    momentum_score: float
    trend_score: float
    risk_score: float
    rs_score: float
    fundamental_score: float


# ─────────────────────────────────────────────
# DETAILED METRICS (UI TABLES)
# structure: {Category: {MetricName: score}}
# ─────────────────────────────────────────────
class MetricsBlock(BaseModel):
    Momentum: Dict[str, float]
    Trend: Dict[str, float]
    Risk: Dict[str, float]
    Relative_Strength: Dict[str, float]
    Fundamental: Dict[str, float]


# ─────────────────────────────────────────────
# POSITION SIZING OUTPUT
# ─────────────────────────────────────────────
class PositionSize(BaseModel):
    label: str
    pct: float


# ─────────────────────────────────────────────
# FINAL SIGNAL OBJECT (SINGLE SOURCE OF TRUTH)
# ─────────────────────────────────────────────
class SignalResponse(BaseModel):
    ticker: str
    price: float

    sector: str
    earnings_date: str
    data_as_of: str

    conviction: float
    verdict: str
    entry_flag: str

    factor_scores: FactorScores
    metrics: MetricsBlock
    raw: RawData

    position_size: PositionSize

    warnings: List[str] = []