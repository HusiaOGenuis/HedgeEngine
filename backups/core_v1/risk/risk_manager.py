class RiskManager:

    def validate_trade(self, signal):
        if signal["expected_value"] <= 0:
            return False
        return True
