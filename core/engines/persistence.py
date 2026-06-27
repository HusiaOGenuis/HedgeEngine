import json
from core.engines.learning_store import trade_log

def save_trade_log():
    with open("trade_log.json", "w") as f:
        json.dump(trade_log, f)

def load_trade_log():
    global trade_log
    try:
        with open("trade_log.json", "r") as f:
            trade_log.extend(json.load(f))
    except:
        pass
