def compute_calibration():

    from core.engines.learning_store import trade_log

    stats = {}

    for t in trade_log:

        sym = t["symbol"]

        if sym not in stats:
            stats[sym] = {
                "error_sum": 0,
                "count": 0
            }

        if t.get("error") is not None:
            stats[sym]["error_sum"] += t["error"]
            stats[sym]["count"] += 1

    adjustments = {}

    for sym, s in stats.items():
        if s["count"] > 0:
            adjustments[sym] = s["error_sum"] / s["count"]

    return adjustments
