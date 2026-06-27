content = """\
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
"""

import os
os.makedirs("core/engines", exist_ok=True)

with open("core/engines/decision_engine.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ DecisionEngine rebuilt with confidence output")
