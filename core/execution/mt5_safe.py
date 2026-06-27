import MetaTrader5 as mt5

class MT5Safe:

    def __init__(self):
        if not mt5.initialize():
            raise Exception("MT5 init failed")

    def execute(self, result):

        symbol = result.get("symbol")
        volume = result.get("volume", 0.1)
        direction = result.get("direction", "BUY")

        order_type = 0 if direction == "BUY" else 1

        print(f"[EXECUTION] {symbol} | {direction} | VOL={volume}")

        request = {
            "action": 1,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": 0,
            "sl": result.get("sl"),
            "tp": result.get("tp"),
            "deviation": 10,
            "magic": 999001,
            "comment": f"HedgeEngine|{symbol}|{direction}"
        }

        print(request)
