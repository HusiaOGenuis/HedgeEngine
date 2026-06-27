import pandas as pd

df = pd.read_csv("..\\Results\\trade_ledger.csv")

df["equity"] = df["pnl"].cumsum()

peak = df["equity"].cummax()
drawdown = (df["equity"] - peak) / peak

print("\n=== RISK DASHBOARD ===")
print(f"Total PnL: {df['pnl'].sum():,.2f}")
print(f"Max Drawdown: {drawdown.min()*100:.2f}%")
print(f"Win Rate: {(df['pnl']>0).mean()*100:.2f}%")