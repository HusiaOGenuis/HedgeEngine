from core.strategy_registry import StrategyRegistry

class MultiStrategyEngine:

    def __init__(self):
        self.registry = StrategyRegistry()

    def run(self, signals):

        results = []

        for s in signals:
            strat = self.registry.get(s["strategy"])
            if strat:
                results.append(strat.process(s))

        return results