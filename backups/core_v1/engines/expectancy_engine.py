def compute_trade_expectancy(signal):

    score = signal.get("signal_score", 0.5)
    dna = signal.get("asset_dna", 0.5)

    # ✅ win probability model
    signal["expected_win_prob"] = min(0.9, 0.4 + score * 0.5)

    # ✅ reward-to-risk model
    signal["expected_rr"] = 1.0 + dna * 1.5

    p = signal["expected_win_prob"]
    rr = signal["expected_rr"]

    # ✅ EV formula
    signal["expected_value"] = (p * rr) - (1 - p)

    return signal
