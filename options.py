import numpy as np

def compute_options_overlay(ticker, price, earnings_date, volatility=0.25):
    # crude but effective regime logic

    iv_rank = min(100, max(0, volatility * 100))

    earnings_risk = earnings_date != "Unknown"

    expected_move = price * volatility * 0.5

    if earnings_risk and iv_rank > 70:
        strategy = "Avoid / wait (IV crush risk)"
        score_adj = -10
    elif iv_rank < 30:
        strategy = "Long premium (calls/puts or debit spreads)"
        score_adj = +5
    else:
        strategy = "Neutral (defined risk spreads preferred)"
        score_adj = 0

    return {
        "iv_rank": iv_rank,
        "earnings_risk": earnings_risk,
        "expected_move": expected_move,
        "strategy": strategy,
        "conviction_adjustment": score_adj
    }