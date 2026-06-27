class DecisionEngine:

    def evaluate(self, signal):

        ev = signal.get("expected_value", 0)

        if ev <= 0:
            return "REJECT", "LOW", 0.0

        elif ev < 0.03:
            return "WATCH", "LOW", 0.005

        elif ev < 0.07:
            return "EXECUTE", "MODERATE", 0.01

        elif ev < 0.15:
            return "EXECUTE", "HIGH", 0.015

        else:
            return "AGGRESSIVE EXECUTE", "VERY HIGH", 0.02
