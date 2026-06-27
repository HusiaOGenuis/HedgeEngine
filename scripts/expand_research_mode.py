import os

code = """\
import time
import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import SignalPipeline
from core.execution.mt5_safe import MT5Safe

# =============================
# RESEARCH MODE SETTINGS
# =============================
SYMBOLS = [
    "EURUSD","GBPUSD","USDJPY","USDCHF",
    "AUDUSD","NZDUSD","USDCAD",
    "EURGBP","EURJPY","GBPJPY",
    "XAUUSD","XAGUSD",
    "BTCUSD","ETHUSD",
    "SPX500","NAS100"
]

MAX_TRADES = 500   # 🔥 EXPANDED
COOLDOWN_SECONDS = 1  # 🔥 FAST LOOP (research mode)

pipeline = SignalPipeline()
executor = MT5Safe()

trade_count = 0

# =============================
# CSV LOGGER
# =============================
file_path = "results_ev_tracking.csv"

if not os.path.exists(file_path):
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol", "ev", "confidence"])

# =============================
# BUILD SIGNAL
# =============================
def build_signal(symbol):
    return {
        "symbol": symbol,
        "signal_score": 0.64,
        "atr_percentile": 0.7,
        "correlation": 0.18,
        "asset_dna": 0.6,
        "session_quality": 1.0,
        "market_regime": 0.8,
        "portfolio_context": 0.5
    }

# =============================
# MAIN LOOP
# =============================
while True:

    if trade_count >= MAX_TRADES:
        print("✅ RESEARCH COMPLETE")
        break

    for symbol in SYMBOLS:

        signal = build_signal(symbol)

        result = pipeline.process(signal)

        ev = float(result["expected_value"])
        conf = result["confidence"]

        # ✅ LOG DATA
        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([symbol, ev, conf])

        # ✅ Only execute HIGH / VERY HIGH
        if result["decision"] == "REJECT":
            continue

        executor.execute(result)

        trade_count += 1

        print("TRADE:", symbol, "EV:", round(ev,4), "CONF:", conf)

    time.sleep(COOLDOWN_SECONDS)
"""

with open("scripts/live_safe.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ RESEARCH MODE INSTALLED (HIGH VOLUME)")