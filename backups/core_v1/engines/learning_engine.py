def update_win_rates():

    from core.engines.learning_store import trade_log

    stats = {}

    for t in trade_log:
        sym = t["symbol"]

        if sym not in stats:
            stats[sym] = {"wins": 0, "total": 0}

        if t["outcome"] is not None:
            stats[sym]["total"] += 1
            stats[sym]["wins"] += t["outcome"]

    win_rates = {}

    for sym, s in stats.items():
        if s["total"] > 0:
            win_rates[sym] = s["wins"] / s["total"]

    return win_rates
