class KellyAllocator:

    def size(self, ev, variance, max_risk=0.02):

        if variance == 0:
            return 0

        kelly = ev / variance

        # Clamp to safe range
        kelly = max(0, min(kelly, 1))

        return kelly * max_risk