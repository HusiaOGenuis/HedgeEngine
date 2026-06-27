import pandas as pd
import numpy as np

class EVCalibrator:

    def __init__(self, path="../Results/trade_ledger.csv"):
        self.df = pd.read_csv(path)

    def create_bins(self):
        self.df["score_bin"] = pd.cut(
            self.df["signal_score"],
            bins=[0.5, 0.55, 0.6, 0.65, 1.0]
        )

    def compute_stats(self):
        stats = []

        for name, group in self.df.groupby("score_bin"):
            wins = group[group["pnl"] > 0]
            losses = group[group["pnl"] <= 0]

            if len(group) == 0:
                continue

            win_rate = len(wins) / len(group)

            avg_win = wins["pnl"].mean() if len(wins) > 0 else 0
            avg_loss = abs(losses["pnl"].mean()) if len(losses) > 0 else 1

            rr = avg_win / avg_loss if avg_loss != 0 else 0

            ev = (win_rate * rr) - (1 - win_rate)

            stats.append({
                "bin": str(name),
                "win_rate": win_rate,
                "rr": rr,
                "ev": ev,
                "count": len(group)
            })

        return pd.DataFrame(stats)

if __name__ == "__main__":
    calibrator = EVCalibrator()
    calibrator.create_bins()
    results = calibrator.compute_stats()

    print("\n=== EMPIRICAL EV TABLE ===")
    print(results)
