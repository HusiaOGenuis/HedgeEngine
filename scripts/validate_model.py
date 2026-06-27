import pandas as pd

df = pd.read_csv("..\\Results\\trade_ledger.csv")

df["score_bin"] = pd.cut(
    df["signal_score"],
    bins=[0.5, 0.55, 0.6, 0.65, 1.0]
)

results = []

for name, group in df.groupby("score_bin"):
    win_rate = (group["pnl"] > 0).mean()

    profit_factor = (
        group[group["pnl"] > 0]["pnl"].sum() /
        abs(group[group["pnl"] <= 0]["pnl"].sum())
    )

    results.append({
        "bin": str(name),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "count": len(group)
    })

print("\n=== VALIDATION RESULTS ===")
print(pd.DataFrame(results))
