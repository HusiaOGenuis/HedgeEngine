import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import SignalPipeline
from core.execution.mt5_safe import MT5Safe
from core.risk.capital_guard import CapitalGuard

from core.engines.research_adapter import enrich_with_research
from core.engines.expectancy_engine import compute_trade_expectancy
from core.engines.alpha_selector import rank_and_select
from core.engines.portfolio_engine import portfolio_optimize
from core.engines.reinforcement_engine import reinforcement_allocation
from core.engines.regime_engine import detect_regime
from core.engines.learning_store import record_trade
from core.engines.real_outcome_engine import update_real_outcomes
from core.engines.calibration_engine import compute_calibration
from core.engines.readiness_engine import system_ready
from core.engines.signal_filter import is_new_signal

pipeline = SignalPipeline()
executor = MT5Safe()
guard = CapitalGuard()

equity = [1000000]

def fetch_signals():
    return [
        {"symbol": "EURUSD", "signal_score": 0.64},
        {"symbol": "GBPUSD", "signal_score": 0.61},
        {"symbol": "USDJPY", "signal_score": 0.58},
        {"symbol": "AUDUSD", "signal_score": 0.60},
        {"symbol": "USDCAD", "signal_score": 0.57},
        {"symbol": "EURJPY", "signal_score": 0.66},
        {"symbol": "GBPJPY", "signal_score": 0.68},
        {"symbol": "XAUUSD", "signal_score": 0.70},
        {"symbol": "XAGUSD", "signal_score": 0.67},
        {"symbol": "BTCUSD", "signal_score": 0.72},
        {"symbol": "ETHUSD", "signal_score": 0.69},
        {"symbol": "NAS100", "signal_score": 0.71}
    ]

while True:

    if not guard.check(equity):
        break

    raw_signals = fetch_signals()
    processed = []

    for s in raw_signals:

        # ✅ FILTER REPEATED SIGNALS
        if not is_new_signal(s):
            continue

        # ✅ ENRICH + REGIME
        s = enrich_with_research(s)
        s = detect_regime(s)

        # ✅ PIPELINE + EXPECTANCY
        result = pipeline.process(s)
        result = compute_trade_expectancy(result)

        if s.get("market_type") == "MEAN_REVERT":
            result["expected_value"] *= 0.8

        processed.append(result)

    # ✅ CALIBRATION
    adjustments = compute_calibration()

    for r in processed:
        if r["symbol"] in adjustments:
            r["expected_value"] += adjustments[r["symbol"]] * -0.5

    # ✅ SELECTION
    signals = rank_and_select(processed)
    signals = portfolio_optimize(signals)
    signals = reinforcement_allocation(signals)

    executed = set()

    for result in signals:

        symbol = result["symbol"]

        # ✅ AVOID DUPLICATE EXECUTION
        if symbol in executed:
            continue

        executed.add(symbol)

        ev = float(result.get("expected_value", 0))
        result["direction"] = "BUY" if ev > 0 else "SELL"

        # ✅ SYSTEM READINESS
        if not system_ready(result):
            print(f"EDGE DETECTED BUT NOT READY: {symbol}")
            continue

        weight = result.get("allocation_weight", 0.5)
        risk = result.get("recommended_risk", 0.01)

        result["volume"] = round(min(0.3, weight * risk * 20), 2)

        result["sl"] = -50
        result["tp"] = 100

        if result["decision"] != "REJECT":
            print(f"[PIPELINE] {symbol} | {result['direction']} | EV={ev:.4f}")
            executor.execute(result)
            record_trade(result)

        print("LIVE:", result)

    # ✅ REAL LEARNING
    update_real_outcomes()

    time.sleep(60)
