# ============================================================
# STRATEGY DASHBOARD (CONTROL PANEL)
# ============================================================

TP_TARGET = 2.0              # Take-profit (currency units)
RISK_PER_TRADE = 0.01        # 1% of equity per trade
MAX_POSITIONS = 5            # Cap open trades
ENABLE_SHORTS = True         # Allow SELL trades

from execution_engine import ExecutionEngine
engine = ExecutionEngine()

import MetaTrader5 as mt5


def get_valid_volume(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"X Symbol info not found: {symbol}")
        return 0.0

    min_vol = info.volume_min
    max_vol = info.volume_max
    step = info.volume_step

    # Always use minimum valid volume (SAFE)
    volume = min_vol

    # Normalize to step size
    volume = round(volume / step) * step

    # Safety clamp
    volume = max(min_vol, min(volume, max_vol))

    return float(volume)


def place_order(symbol, volume=None, direction=1):
    smart_execute(symbol, direction)


def already_open(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return False
    return len(positions) > 0


# ============================================================
# FULL AUTO EXECUTION OVERRIDE (DROP-IN)
# ============================================================

import MetaTrader5 as mt5


def smart_execute(symbol, direction):
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"X Symbol not found: {symbol}")
        return

    # AUTO VOLUME (broker-correct)


# ============================================================
# SMART POSITION CONTROL (FULL UPGRADE)
# ============================================================

import MetaTrader5 as mt5
from datetime import datetime

# GLOBAL POSITION MEMORY (no files needed)
POSITION_MEMORY = {}


def smart_execute(symbol, direction):
    tick = mt5.symbol_info_tick(symbol)
    info = mt5.symbol_info(symbol)
    if tick is None or info is None:
        print(f"DATA ERROR: {symbol}")
        return

    volume = info.volume_min

    # Normalize volume
    step = info.volume_step
    volume = round(volume / step) * step
    volume = float(volume)

    price = tick.ask if direction == 1 else tick.bid

    positions = mt5.positions_get(symbol=symbol)

    if positions:
        pos = positions[0]
        profit = pos.profit

        # IF SIGNAL REVERSES → CLOSE CURRENT POSITION
        # BUY (0) vs SELL (1)
        if (pos.type == 0 and direction == -1) or (pos.type == 1 and direction == 1):
            close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            close_price = tick.bid if pos.type == 0 else tick.ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": close_price,
                "deviation": 20,
                "magic": 888,
                "comment": "REVERSAL",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            result = mt5.order_send(request)
            print(f"REVERSAL CLOSE {symbol} | profit={profit}")
            # REMOVED 'return' - allows execution to continue to entry block

        # TAKE PROFIT
        if profit >= TP_TARGET:
            close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            close_price = tick.bid if pos.type == 0 else tick.ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": close_price,
                "deviation": 20,
                "magic": 888,
                "comment": "TP_EXIT",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            result = mt5.order_send(request)
            print(f"EXIT {symbol} | profit={profit}")
            return

        print(f"HOLD {symbol} | profit={profit}")
        return

    # After reversal close, re-check positions to ensure entry can proceed
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        return

    # ============================================================
    # NEW ENTRY ONLY IF NO POSITION
    # ============================================================

    account = mt5.account_info()
    if not account:
        print(f"ACCOUNT DATA ERROR: {symbol}")
        return

    equity = account.equity

    # SMART POSITION SIZING
    risk_amount = equity * RISK_PER_TRADE
    contract_size = info.trade_contract_size if info.trade_contract_size > 0 else 1
    volume = risk_amount / contract_size

    step = info.volume_step
    volume = round(volume / step) * step
    volume = max(info.volume_min, min(volume, info.volume_max))
    volume = float(volume)

    price = tick.ask if direction == 1 else tick.bid

    # LIMIT TOTAL POSITIONS
    if mt5.positions_total() >= MAX_POSITIONS:
        print("MAX POSITIONS REACHED")
        return

    if direction == -1 and not ENABLE_SHORTS:
        print(f"SHORTS DISABLED: {symbol}")
        return

    order_type = mt5.ORDER_TYPE_BUY if direction == 1 else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 888,
        "comment": "SMART_ENTRY",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    side = "BUY" if direction == 1 else "SELL"
    print(f"ENTRY {symbol} | {side} | vol={volume} | retcode={result.retcode}")