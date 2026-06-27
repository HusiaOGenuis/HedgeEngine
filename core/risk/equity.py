import numpy as np
import pandas as pd

def compute_equity_curve(df, initial_capital=1_000_000):
    equity = initial_capital
    equity_curve = []

    for pnl in df["pnl"]:
        equity += pnl
        equity_curve.append(equity)

    curve = np.array(equity_curve)
    running_max = np.maximum.accumulate(curve)
    drawdown = (curve - running_max) / running_max

    return curve, drawdown

def compute_max_dd(drawdown):
    return np.min(drawdown) * 100
