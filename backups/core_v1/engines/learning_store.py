import time

trade_log = []

def record_trade(result):

    trade_log.append({
        "symbol": result.get("symbol"),
        "direction": result.get("direction"),
        "ev": float(result.get("expected_value", 0)),
        "win_prob": result.get("expected_win_prob"),
        "rr": result.get("expected_rr"),
        "timestamp": time.time(),
        "outcome": None
    })

    return result
