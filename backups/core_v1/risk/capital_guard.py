class CapitalGuard:

    def __init__(self):
        self.max_dd = -0.20

    def check(self, equity):

        if len(equity) < 2:
            return True

        peak = max(equity)
        current = equity[-1]

        dd = (current - peak) / peak

        if dd < self.max_dd:
            print("STOP: Drawdown breach")
            return False

        return True
