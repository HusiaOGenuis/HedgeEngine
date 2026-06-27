import pandas as pd

df = pd.read_csv("..\\Results\\trade_ledger.csv")

monthly = df.copy()
monthly["month"] = pd.to_datetime(monthly["timestamp"]).dt.to_period("M")

report = monthly.groupby("month")["pnl"].sum()

print("\n=== INVESTOR REPORT ===")
print(report)