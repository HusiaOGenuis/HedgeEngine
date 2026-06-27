import numpy as np

class PortfolioOptimizer:

    def allocate(self, signals):

        weights = []
        
        for s in signals:
            ev = s["expected_value"]
            corr = s.get("correlation", 0)

            weight = max(ev, 0) * (1 - corr)
            weights.append(weight)

        total = sum(weights)

        if total == 0:
            return [0]*len(signals)

        return [w / total for w in weights]