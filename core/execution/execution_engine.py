from core.execution.mt5_bridge import MT5Bridge

class ExecutionEngine:

    def __init__(self):
        self.broker = MT5Bridge()

    def execute(self, signal):
        if signal["decision"] == "REJECT":
            return

        if signal["expected_value"] <= 0:
            return

        self.broker.execute(signal)