import time
from core.pipeline import SignalPipeline
from core.execution.execution_engine import ExecutionEngine

pipeline = SignalPipeline()
executor = ExecutionEngine()

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
    signals = fetch_signals()

    for s in signals:
        result = pipeline.process(s)
        executor.execute(result)

        print("LIVE:", result)

    time.sleep(60)