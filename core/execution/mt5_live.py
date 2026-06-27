import MetaTrader5 as mt5

class MT5Bridge:

    def __init__(self):
        mt5.initialize()

    def execute(self, signal):

        lot = round(signal["recommended_risk"] * 10, 2)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "EURUSD",
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick("EURUSD").ask,
            "deviation": 10,
            "magic": 123456,
            "comment": "HedgeEngine",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        print("MT5 EXECUTION:", result)