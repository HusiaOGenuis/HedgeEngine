import os

with open("scripts/advanced_validation.py", "w", encoding="utf-8") as f:
    f.write("""\
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

df = pd.read_csv("..\\\\Results\\\\trade_ledger.csv")

df["capital_score"] = 0.40 * df["signal_score"] + 0.3

# Spearman
corr = spearmanr(df["capital_score"], df["pnl"])
print("\\nSpearman:", corr.correlation)

# Plot
plt.scatter(df["capital_score"], df["pnl"])
plt.xlabel("Capital Score")
plt.ylabel("PnL")
plt.title("Score vs PnL")

plt.savefig("output/score_vs_pnl.png")
plt.show()
""")

print("✅ Validation system written")