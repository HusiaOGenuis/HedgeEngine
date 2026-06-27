import random

def update_trade_outcomes():

    from core.engines.learning_store import trade_log

    for t in trade_log:
        if t["outcome"] is None:
            p = t["win_prob"] or 0.5
            t["outcome"] = 1 if random.random() < p else 0
