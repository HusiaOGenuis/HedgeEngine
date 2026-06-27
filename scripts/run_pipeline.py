from core.pipeline import SignalPipeline
from core.risk.risk_manager import RiskManager

pipeline = SignalPipeline()
risk_mgr = RiskManager()

signal = {
    "signal_score": 0.64,
    "atr_percentile": 0.7,
    "correlation": 0.18,
    "asset_dna": 0.6,
    "session_quality": 1.0,
    "market_regime": 0.8,
    "portfolio_context": 0.5
}

result = pipeline.process(signal)

decision = result["decision"] if risk_mgr.validate_trade(result) else "REJECT"

print("\n======================================================")
print("TRANSITION CAPITAL HEDGE ENGINE")
print("======================================================")

print(f"\nSignal Score        : {result['signal_score']:.2f}")
print(f"Capital Score       : {result['capital_score']:.3f}")

print(f"\nExpected Value      : {result['expected_value']:.4f} R")

print(f"\nRecommended Risk    : {result['recommended_risk']*100:.2f}%")

print("\nDecision            :", decision)
print("Confidence          :", result["confidence"])

print("\n======================================================")
