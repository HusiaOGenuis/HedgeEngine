import os

# =========================
# CREATE REQUIRED FOLDERS
# =========================
folders = [
    "core",
    "core/engines",
    "core/execution",
    "core/risk",
    "core/learning",
    "scripts",
    "config"
]

for f in folders:
    os.makedirs(f, exist_ok=True)

# Create __init__.py files
for f in ["core", "core/engines", "core/execution", "core/risk", "core/learning"]:
    open(f"{f}/__init__.py", "w").close()

# =========================
# MT5 SAFE EXECUTION
# =========================
mt5_safe = """\
import MetaTrader5 as mt5

class MT5Safe:

    def __init__(self):
        if not mt5.initialize():
            raise Exception("MT5 init failed")

    def execute(self, signal):

        if signal["recommended_risk"] == 0:
            return

        lot = round(signal["recommended_risk"] * 5, 2)

        tick = mt5.symbol_info_tick("EURUSD")

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "EURUSD",
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 10,
            "magic": 999001,
            "comment": "HedgeEngine"
        }

        result = mt5.order_send(request)

        print("EXEC:", result)
"""

open("core/execution/mt5_safe.py", "w", encoding="utf-8").write(mt5_safe)

# =========================
# CAPITAL GUARD
# =========================
capital_guard = """\
class CapitalGuard:

    def __init__(self):
        self.max_dd = -0.20

    def check(self, equity):

        if len(equity) < 2:
            return True

        peak = max(equity)
        current = equity[-1]

        dd = (current - peak) / peak

        if dd < self.max_dd:
            print("STOP: Drawdown breach")
            return False

        return True
"""

open("core/risk/capital_guard.py", "w", encoding="utf-8").write(capital_guard)

# =========================
# SAFE LIVE ENGINE
# =========================
live_engine = """\
import time

from core.pipeline import SignalPipeline
from core.execution.mt5_safe import MT5Safe
from core.risk.capital_guard import CapitalGuard

pipeline = SignalPipeline()
executor = MT5Safe()
guard = CapitalGuard()

equity = [1000000]

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

while True:

    if not guard.check(equity):
        break

    signals = fetch_signals()

    for s in signals:
        result = pipeline.process(s)

        if result["decision"] != "REJECT":
            executor.execute(result)

        print("LIVE:", result)

    time.sleep(60)
"""

open("scripts/live_safe.py", "w", encoding="utf-8").write(live_engine)

print("✅ FULL STRUCTURE + FILES CREATED SUCCESSFULLY")