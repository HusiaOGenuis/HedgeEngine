import streamlit as st
import pandas as pd

# Load path
with open("config/data_path.txt") as f:
    path = f.read().strip()

df = pd.read_csv(path)

st.title("TRANSITION CAPITAL DASHBOARD")

st.metric("Total PnL", f"{df['pnl'].sum():,.0f}")
st.metric("Win Rate", f"{(df['pnl']>0).mean()*100:.2f}%")

df["equity"] = df["pnl"].cumsum()

st.line_chart(df["equity"])
st.scatter_chart(df[["signal_score", "pnl"]])
st.subheader("Risk Metrics")

st.write("Sharpe Ratio (approx):", df["pnl"].mean()/df["pnl"].std())

dd = (df["pnl"].cumsum() - df["pnl"].cumsum().cummax())/df["pnl"].cumsum().cummax()

st.write("Max Drawdown %:", dd.min()*100)