import os

code = """\
import time
import sys
import os
import csv
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import SignalPipeline
from core.execution.mt5_safe import MT5Safe

SYMBOLS = [
    "EURUSD","GBPUSD","USDJPY","USDCHF",
    "AUDUSD","NZDUSD","USDCAD",
    "EURGBP","EURJPY","GBPJPY",
    "XAUUSD","XAGUSD",
    "BTCUSD","ETHUSD",
    "SPX500","NAS100"
]

MAX_TRADES = 500
COOLDOWN_SECONDS = 1

pipeline = SignalPipeline()
executor = MT5Safe()

trade_count = 0

file_path = "results_ev_tracking.csv"

if not os.path.exists(file_path):
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol","ev","confidence"])

def build_signal(symbol):
    return {
        "symbol": symbol,
        "signal_score": random.uniform(0.3, 0.9),
        "atr_percentile": random.uniform(0.2, 0.95),
        "correlation": random.uniform(-0.5, 0.5),
        "asset_dna": random.uniform(0.3, 0.9),
        "session_quality": random.uniform(0.3, 1.0),
        "market_regime": random.uniform(0.2, 1.0),
        "portfolio_context": random.uniform(0.2, 0.9)
    }

while True:

    if trade_count >= MAX_TRADES:
        print("✅ RESEARCH COMPLETE")
        break

    for symbol in SYMBOLS:

        signal = build_signal(symbol)
        result = pipeline.process(signal)

        ev = float(result["expected_value"])
        conf = result["confidence"]

        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([symbol, ev, conf])

        if result["decision"] == "REJECT":
            continue

        executor.execute(result)
        trade_count += 1

        print(symbol, "EV:", round(ev,4), "CONF:", conf)

    time.sleep(COOLDOWN_SECONDS)
"""

with open("scripts/live_safe.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ VARIABILITY INJECTED")