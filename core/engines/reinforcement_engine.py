def reinforcement_allocation(signals):

    from core.engines.learning_store import trade_log

    perf = {}

    for t in trade_log:
        sym = t["symbol"]

        if sym not in perf:
            perf[sym] = {"wins": 0, "total": 0}

        if t["outcome"] is not None:
            perf[sym]["total"] += 1
            perf[sym]["wins"] += t["outcome"]

    weights = {}

    for sym, s in perf.items():
        if s["total"] > 0:
            weights[sym] = s["wins"] / s["total"]
        else:
            weights[sym] = 0.5

    for s in signals:
        sym = s["symbol"]

        base = s.get("capital_score", 0.5)
        reinforce = weights.get(sym, 0.5)

        # ✅ blend model + learning
        s["allocation_weight"] = 0.5 * base + 0.5 * reinforce

    return signals
