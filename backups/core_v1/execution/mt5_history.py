import MetaTrader5 as mt5
from datetime import datetime, timedelta

def fetch_trade_history():

    end = datetime.now()
    start = end - timedelta(days=1)

    deals = mt5.history_deals_get(start, end)

    results = []

    if deals:
        for d in deals:

            results.append({
                "symbol": d.symbol,
                "profit": d.profit,
                "volume": d.volume,
                "price": d.price,
                "time": d.time
            })

    return results
