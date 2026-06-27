class RegimeSwitch:

    def detect(self, volatility):

        if volatility < 0.3:
            return "LOW_VOL"

        elif volatility < 0.7:
            return "NORMAL"

        else:
            return "HIGH_VOL"