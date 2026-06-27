import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os

df = pd.read_csv("..\\Results\\trade_ledger.csv")

# Feature
X = df["signal_score"].values.reshape(-1, 1)
y = df["pnl"].values

# Fit model
model = LinearRegression()
model.fit(X, y)

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/ev_model.pkl")

print("\n✅ Continuous EV model trained and saved")
print("Coefficient:", model.coef_[0])
print("Intercept:", model.intercept_)