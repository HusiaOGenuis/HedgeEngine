from core.engines.ev_engine import EVEngine
from core.engines.decision_engine import DecisionEngine
from core.engines.allocator import CapitalAllocator

class SignalPipeline:

    def __init__(self):
        self.ev_engine = EVEngine()
        self.decision_engine = DecisionEngine()
        self.allocator = CapitalAllocator()

    def process(self, signal):

        ev_data = self.ev_engine.evaluate_signal(signal)
        signal.update(ev_data)

        decision, confidence, risk = self.decision_engine.evaluate(signal)

        alloc = self.allocator.compute_capital_score(signal)

        return {
            **signal,
            "decision": decision,
            "confidence": confidence,
            "recommended_risk": risk,
            "capital_score": alloc
        }
