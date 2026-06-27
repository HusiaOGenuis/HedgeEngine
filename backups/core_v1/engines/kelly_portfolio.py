class KellyPortfolio:

    def size(self, ev, variance, cap=0.02):

        if variance <= 0:
            return 0

        kelly = ev / variance

        kelly = max(0, min(kelly, 1))

        return kelly * cap