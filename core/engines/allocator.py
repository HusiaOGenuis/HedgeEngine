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
