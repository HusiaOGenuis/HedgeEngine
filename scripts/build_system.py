import os

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# =============================
# EV ENGINE
# =============================
write("core/engines/ev_engine.py", """\
class EVEngine:

    def __init__(self):
        self.ev_table = [
            {"min": 0.50, "max": 0.55, "win_rate": 0.2649, "rr": 1.78, "ev": -0.26},
            {"min": 0.55, "max": 0.60, "win_rate": 0.2882, "rr": 2.72, "ev": 0.07},
            {"min": 0.60, "max": 0.65, "win_rate": 0.3198, "rr": 2.70, "ev": 0.18},
            {"min": 0.65, "max": 1.00, "win_rate": 0.4344, "rr": 2.01, "ev": 0.31}
        ]

    def lookup(self, score):
        for row in self.ev_table:
            if row["min"] < score <= row["max"]:
                return row
        return None

    def evaluate_signal(self, signal):
        row = self.lookup(signal["signal_score"])

        if row is None:
            return {"expected_value": -1}

        ev_adj = row["ev"] * (1 - signal["correlation"])

        return {
            "expected_win_prob": row["win_rate"],
            "expected_rr": row["rr"],
            "expected_value": ev_adj
        }
""")

# =============================
# ALLOCATOR (DETERMINISTIC)
# =============================
write("core/engines/allocator.py", """\
class CapitalAllocator:

    def compute_capital_score(self, signal):
        return (
            0.40 * signal["signal_score"] +
            0.25 * signal["asset_dna"] +
            0.20 * signal["session_quality"] +
            0.10 * signal["market_regime"] +
            0.05 * signal["portfolio_context"]
        )

    def decision_policy(self, score):
        if score < 0.55:
            return "REJECT", 0.0
        elif score < 0.60:
            return "WATCH", 0.005
        elif score < 0.65:
            return "EXECUTE", 0.01
        elif score < 0.75:
            return "EXECUTE", 0.015
        else:
            return "AGGRESSIVE EXECUTE", 0.02

    def allocate(self, signal):
        score = self.compute_capital_score(signal)
        decision, risk = self.decision_policy(score)

        return {
            "capital_score": score,
            "decision": decision,
            "recommended_risk": risk
        }
""")

# =============================
# PIPELINE
# =============================
write("core/pipeline.py", """\
from core.engines.ev_engine import EVEngine
from core.engines.allocator import CapitalAllocator

class SignalPipeline:

    def __init__(self):
        self.ev_engine = EVEngine()
        self.allocator = CapitalAllocator()

    def process(self, signal):
        ev_data = self.ev_engine.evaluate_signal(signal)
        alloc_data = self.allocator.allocate(signal)

        return {**signal, **ev_data, **alloc_data}
""")

# =============================
# RISK ENGINE
# =============================
write("core/risk/risk_manager.py", """\
class RiskManager:

    def validate_trade(self, signal):
        if signal["expected_value"] <= 0:
            return False
        return True
""")

# =============================
# RUN PIPELINE
# =============================
write("scripts/run_pipeline.py", """\
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

print("\\n======================================================")
print("TRANSITION CAPITAL HEDGE ENGINE")
print("======================================================")

print(f"\\nSignal Score        : {result['signal_score']:.2f}")
print(f"Capital Score       : {result['capital_score']:.3f}")

print(f"\\nExpected Win Rate   : {result['expected_win_prob']*100:.1f}%")
print(f"Expected RR         : {result['expected_rr']:.2f}")
print(f"\\nExpected Value      : {result['expected_value']:.2f}R")

print(f"\\nRecommended Risk    : {result['recommended_risk']*100:.2f}%")

print("\\nDecision            :", decision)
print("Confidence          :", "HIGH" if result["capital_score"] > 0.65 else "MODERATE")

print("\\n======================================================")
""")

print("\\n✅ SYSTEM BUILT SUCCESSFULLY")