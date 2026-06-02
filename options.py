# options.py — WhaleWatch Options Overlay

def options_overlay(signal):
    c = signal.conviction
    r = signal.risk_score
    v = signal.factor_scores.volatility if hasattr(signal.factor_scores, "volatility") else 50

    # regime logic
    iv_regime = (
        "HIGH" if v > 70 else
        "NORMAL" if v > 40 else
        "LOW"
    )

    # direction bias
    bias = (
        "CALL BIAS" if c > 70 and r < 60 else
        "PUT HEDGE" if r > 70 else
        "NO TRADE"
    )

    # structure suggestion
    if bias == "CALL BIAS":
        return {
            "strategy": "CALL SPREAD",
            "note": "defined risk bullish structure",
            "iv": iv_regime
        }

    if bias == "PUT HEDGE":
        return {
            "strategy": "PUT SPREAD / HEDGE",
            "note": "protect downside exposure",
            "iv": iv_regime
        }

    return {
        "strategy": "NO OPTIONS TRADE",
        "note": "edge not sufficient",
        "iv": iv_regime
    }