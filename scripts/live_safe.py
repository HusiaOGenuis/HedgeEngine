import time
import MetaTrader5 as mt5

from config.synthetic_basket import synthetic_assets
from core.execution.mt5_live_real import connect_mt5, get_account
from core.engines.portfolio_engine_v2 import portfolio_intelligence
from core.engines.signal_generator import generate_signal
from core.execution.executor_wrapper import execute_signals

print("✅ ENGINE STARTED")

if not connect_mt5():
    print("❌ MT5 CONNECTION FAILED")
    quit()

print("✅ MT5 CONNECTED")
account = mt5.account_info()
print(f"✅ ACCOUNT: {account.login} | Equity: {account.equity}")
equity_curve = []
cycle = 0

while True:

    cycle += 1
    print(f"\n======================")
    print(f"CYCLE {cycle}")
    print(f"======================")

    signals = []

    # ✅ GENERATE RICH SIGNALS
    for asset in synthetic_assets:
        signal = generate_signal(asset)
        if signal:
            signals.append(signal)

    print(f"Assets scanned: {len(signals)}")

    # ✅ PORTFOLIO FILTERING
    signals = portfolio_intelligence(signals, equity_curve)

    print(f"Selected trades: {len(signals)}")

    for s in signals:
        print(f"→ {s['symbol']} | EV={round(s['expected_value'],3)} | dir={s['direction']}")

    # ✅ EXECUTION
    if len(signals) > 0:
        execute_signals(signals)

    # ✅ EQUITY TRACKING
    acc = get_account()
    if acc:
        eq = acc["equity"]
        equity_curve.append(eq)
        print(f"Equity: {eq}")

    time.sleep(5)
