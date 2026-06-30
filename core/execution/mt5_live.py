import MetaTrader5 as mt5

def get_open_positions():

    positions = mt5.positions_get()

    data = []

    if positions:
        for p in positions:
            data.append({
                "symbol": p.symbol,
                "volume": p.volume,
                "price_open": p.price_open,
                "current_price": p.price_current,
                "profit": p.profit
            })

    return data


def get_account_info():

    acc = mt5.account_info()

    if not acc:
        return {}

    return {
        "balance": acc.balance,
        "equity": acc.equity,
        "margin": acc.margin,
        "free_margin": acc.margin_free
    }
