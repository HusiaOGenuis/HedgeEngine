content = """\
from core.engines.decision_engine import DecisionEngine

class SignalPipeline:

    def __init__(self):
        from core.engines.ev_engine import EVEngine
        from core.engines.allocator import CapitalAllocator

        self.ev_engine = EVEngine()
        self.allocator = CapitalAllocator()
        self.decision_engine = DecisionEngine()

    def process(self, signal):

        ev_data = self.ev_engine.evaluate_signal(signal)
        signal.update(ev_data)

        decision, confidence, risk = self.decision_engine.evaluate(signal)

        signal.update({
            "decision": decision,
            "confidence": confidence,
            "recommended_risk": risk
        })

        return signal
"""
open("core/pipeline.py", "w").write(content)

print("✅ Decision layer aligned with EV")