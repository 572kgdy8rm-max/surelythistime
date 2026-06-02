# schema.py

from typing import TypedDict, Dict, Any, List, Optional

class SignalOutput(TypedDict):
    ticker: str
    price: float
    sector: str
    earnings_date: str

    conviction: float
    verdict: str
    entry_flag: str
    position_size: Dict[str, Any]

    metrics: Dict[str, Dict[str, float]]
    scores: Dict[str, float]
    raw: Dict[str, Any]

    options: Dict[str, Any]
    warnings: List[str]
    data_as_of: str