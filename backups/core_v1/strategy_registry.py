class StrategyRegistry:

    def __init__(self):
        self.strategies = {}

    def register(self, name, strategy):
        self.strategies[name] = strategy

    def get(self, name):
        return self.strategies.get(name)