code = """\
import time
import sys
import os

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import SignalPipeline
from core.execution.mt5_safe import MT5Safe

# =============================
# CONTROL SETTINGS
# =============================
MAX_TRADES = 3
COOLDOWN_SECONDS = 60
MAX_DRAWDOWN = -0.10

START_CAPITAL = 100000
equity = START_CAPITAL
peak = START_CAPITAL

# =============================
# INIT
# =============================
pipeline = SignalPipeline()
executor = MT5Safe()

trade_count = 0

def fetch_signals():
    return [{
        "signal_score": 0.64,
        "atr_percentile": 0.7,
        "correlation": 0.18,
        "asset_dna": 0.6,
        "session_quality": 1.0,
        "market_regime": 0.8,
        "portfolio_context": 0.5
    }]

# =============================
# MAIN LOOP
# =============================
while True:

    if trade_count >= MAX_TRADES:
        print("STOP: Max trades reached")
        break

    signals = fetch_signals()

    for s in signals:

        result = pipeline.process(s)

        # ✅ simulate pnl
        pnl = result["expected_value"] * 1000
        equity += pnl

        if equity > peak:
            peak = equity

        dd = (equity - peak) / peak

        print("EQUITY:", round(equity, 2), "DD:", round(dd, 4))

        # ✅ kill switch
        if dd < MAX_DRAWDOWN:
            print("KILL SWITCH ACTIVATED")
            exit()

        # ✅ execution
        if result["decision"] != "REJECT":
            executor.execute(result)
            trade_count += 1

        print("LIVE:", result)

    time.sleep(COOLDOWN_SECONDS)
"""

with open("scripts/live_safe.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ CONTROL LAYER FIXED SUCCESSFULLY")
