# ============================================================
# STRATEGY DASHBOARD (CONTROL PANEL)
# ============================================================

TP_TARGET = 2.0              # Take-profit (currency units)
RISK_PER_TRADE = 0.01        # 1% of equity per trade
MAX_POSITIONS = 5            # Cap open trades
ENABLE_SHORTS = True         # Allow SELL trades

# ============================================================
# SINGLE SOURCE OF TRUTH - CANONICAL EXECUTOR
# ============================================================
import MetaTrader5 as mt5
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# SINGLE IMPORT - from the canonical location only
from core.execution.order_executor import place_order, smart_execute, execution_engine

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_valid_volume(symbol: str) -> float:
    """
    Get the minimum valid volume for a symbol (SAFE mode)
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Minimum valid volume as float
    """
    info = mt5.symbol_info(symbol)
    if info is None:
        logging.error(f"Symbol info not found: {symbol}")
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


def already_open(symbol: str) -> bool:
    """
    Check if a position is already open for the symbol
    
    Args:
        symbol: Trading symbol
        
    Returns:
        True if position exists, False otherwise
    """
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return False
    return len(positions) > 0


def get_position_profit(symbol: str) -> Optional[float]:
    """
    Get current profit for an open position
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Profit as float, or None if no position
    """
    positions = mt5.positions_get(symbol=symbol)
    if positions and len(positions) > 0:
        return positions[0].profit
    return None


def close_position(symbol: str, reason: str = "CLOSE") -> bool:
    """
    Close an open position
    
    Args:
        symbol: Trading symbol
        reason: Reason for closing (for logging)
        
    Returns:
        True if closed successfully
    """
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        logging.warning(f"No position to close: {symbol}")
        return False
    
    pos = positions[0]
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logging.error(f"No tick data for {symbol}")
        return False
    
    # Determine close direction
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
        "comment": reason,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    result = mt5.order_send(request)
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        logging.info(f"CLOSED {symbol} | profit={pos.profit:.2f} | reason={reason}")
        return True
    else:
        logging.error(f"FAILED TO CLOSE {symbol} | retcode={result.retcode if result else 'None'}")
        return False


def calculate_position_size(symbol: str, equity: float, risk_per_trade: float) -> float:
    """
    Calculate position size based on risk management
    
    Args:
        symbol: Trading symbol
        equity: Current equity
        risk_per_trade: Risk as percentage of equity (0.01 = 1%)
        
    Returns:
        Calculated volume
    """
    info = mt5.symbol_info(symbol)
    if info is None:
        logging.error(f"Symbol info not found: {symbol}")
        return 0.0
    
    contract_size = info.trade_contract_size if info.trade_contract_size > 0 else 1
    risk_amount = equity * risk_per_trade
    volume = risk_amount / contract_size
    
    # Normalize to step size
    step = info.volume_step
    volume = round(volume / step) * step
    
    # Clamp to allowed range
    volume = max(info.volume_min, min(volume, info.volume_max))
    
    return float(volume)


# ============================================================
# SMART EXECUTION - SINGLE DEFINITION
# ============================================================

def smart_execute(symbol: str, direction: int) -> bool:
    """
    Smart position management with full lifecycle control
    
    Args:
        symbol: Trading symbol
        direction: 1 = BUY, -1 = SELL
        
    Returns:
        True if successful, False otherwise
    """
    # Validate inputs
    if direction not in [1, -1]:
        logging.error(f"Invalid direction: {direction}. Must be 1 (BUY) or -1 (SELL)")
        return False
    
    # Get market data
    tick = mt5.symbol_info_tick(symbol)
    info = mt5.symbol_info(symbol)
    if tick is None or info is None:
        logging.error(f"DATA ERROR: {symbol}")
        return False
    
    # Check if position exists
    positions = mt5.positions_get(symbol=symbol)
    
    if positions and len(positions) > 0:
        pos = positions[0]
        profit = pos.profit
        
        # ============================================================
        # REVERSAL LOGIC - Close if signal reverses
        # ============================================================
        # pos.type: 0 = BUY, 1 = SELL
        if (pos.type == 0 and direction == -1) or (pos.type == 1 and direction == 1):
            if close_position(symbol, "REVERSAL"):
                logging.info(f"REVERSAL CLOSE {symbol} | profit={profit:.2f}")
                # After reversal, allow new entry to proceed
            else:
                logging.error(f"REVERSAL FAILED {symbol}")
                return False
        
        # ============================================================
        # TAKE PROFIT LOGIC
        # ============================================================
        elif profit >= TP_TARGET:
            if close_position(symbol, "TP_EXIT"):
                logging.info(f"TP EXIT {symbol} | profit={profit:.2f}")
                return True
            else:
                logging.error(f"TP EXIT FAILED {symbol}")
                return False
        
        # ============================================================
        # HOLD POSITION
        # ============================================================
        else:
            logging.info(f"HOLD {symbol} | profit={profit:.2f} | vol={pos.volume}")
            return True
    
    # ============================================================
    # NEW ENTRY - Only if no position after reversal check
    # ============================================================
    
    # Re-check positions after potential reversal close
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        logging.debug(f"Position exists after reversal check: {symbol}")
        return True
    
    # Get account info
    account = mt5.account_info()
    if not account:
        logging.error(f"ACCOUNT DATA ERROR: {symbol}")
        return False
    
    # ============================================================
    # POSITION SIZING with risk management
    # ============================================================
    equity = account.equity
    volume = calculate_position_size(symbol, equity, RISK_PER_TRADE)
    
    if volume <= 0:
        logging.error(f"Invalid volume calculated: {volume}")
        return False
    
    # ============================================================
    # LIMIT TOTAL POSITIONS
    # ============================================================
    total_positions = mt5.positions_total()
    if total_positions >= MAX_POSITIONS:
        logging.warning(f"MAX POSITIONS REACHED: {total_positions}/{MAX_POSITIONS}")
        return False
    
    # ============================================================
    # SHORT CHECK
    # ============================================================
    if direction == -1 and not ENABLE_SHORTS:
        logging.warning(f"SHORTS DISABLED: {symbol}")
        return False
    
    # ============================================================
    # EXECUTE ORDER using canonical executor
    # ============================================================
    price = tick.ask if direction == 1 else tick.bid
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
    
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        logging.info(f"ENTRY {symbol} | {side} | vol={volume:.4f} | price={price:.5f}")
        return True
    else:
        logging.error(f"ENTRY FAILED {symbol} | {side} | retcode={result.retcode if result else 'None'}")
        return False


# ============================================================
# MAIN EXECUTION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize MT5 if needed
    if not mt5.initialize():
        logging.error("MT5 initialization failed!")
        exit(1)
    
    logging.info("Strategy Dashboard initialized successfully")
    logging.info(f"TP_TARGET: {TP_TARGET}, RISK_PER_TRADE: {RISK_PER_TRADE}")
    logging.info(f"MAX_POSITIONS: {MAX_POSITIONS}, ENABLE_SHORTS: {ENABLE_SHORTS}")