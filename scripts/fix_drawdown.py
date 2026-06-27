import pandas as pd
import numpy as np

df = pd.read_csv("..\\Results\\trade_ledger.csv")

initial = 1_000_000

equity = initial + df["pnl"].cumsum()

running_max = equity.cummax()
drawdown = (equity - running_max) / running_max

print("\n✅ FIXED DRAWDOWN")
print(f"Max DD: {drawdown.min()*100:.2f}%")