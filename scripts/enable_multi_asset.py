content = """\
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import SignalPipeline
from core.execution.mt5_safe import MT5Safe

# =============================
# SETTINGS
# =============================
SYMBOLS = [
    "EURUSD","GBPUSD","USDJPY","USDCHF",
    "AUDUSD","NZDUSD","USDCAD",
    "EURGBP","EURJPY","GBPJPY",
    "XAUUSD","XAGUSD",
    "BTCUSD","ETHUSD",
    "SPX500","NAS100"
]

MAX_TRADES = 6
COOLDOWN_SECONDS = 60

pipeline = SignalPipeline()
executor = MT5Safe()

trade_count = 0

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

while True:

    if trade_count >= MAX_TRADES:
        print("STOP: Max trades reached")
        break

    for symbol in SYMBOLS:

        signal = build_signal(symbol)

        result = pipeline.process(signal)

        if result["decision"] == "REJECT":
            continue

        executor.execute(result)
        trade_count += 1

        print("TRADE:", symbol, result["expected_value"], result["confidence"])

    time.sleep(COOLDOWN_SECONDS)
"""

with open("scripts/live_safe.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ MULTI-ASSET ENGINE ACTIVATED")