def detect_regime(signal):

    atr = signal.get("atr_percentile", 0.5)
    score = signal.get("signal_score", 0.5)

    # ✅ volatility regime
    if atr > 0.8:
        signal["volatility_regime"] = "HIGH"
    elif atr < 0.4:
        signal["volatility_regime"] = "LOW"
    else:
        signal["volatility_regime"] = "NORMAL"

    # ✅ market behaviour regime
    if score > 0.65:
        signal["market_type"] = "TREND"
    elif score < 0.55:
        signal["market_type"] = "MEAN_REVERT"
    else:
        signal["market_type"] = "NEUTRAL"

    return signal
