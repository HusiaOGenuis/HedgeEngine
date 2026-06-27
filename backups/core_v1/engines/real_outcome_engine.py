def update_real_outcomes():

    from core.engines.learning_store import trade_log
    from core.execution.mt5_history import fetch_trade_history

    history = fetch_trade_history()

    for h in history:
        for t in trade_log:

            if t["symbol"] == h["symbol"] and t["outcome"] is None:

                # ✅ real outcome from broker
                t["outcome"] = 1 if h["profit"] > 0 else 0

                t["realized_rr"] = h["profit"]

                # ✅ REAL ERROR (not simulated)
                t["error"] = t["realized_rr"] - t["predicted_ev"]
