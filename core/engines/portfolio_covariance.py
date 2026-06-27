import numpy as np

class PortfolioOptimizer:

    def optimize(self, returns_matrix):

        cov = np.cov(returns_matrix)

        inv_cov = np.linalg.pinv(cov)

        ones = np.ones(len(cov))

        weights = inv_cov @ ones
        weights /= (ones.T @ inv_cov @ ones)

        return weights