content = """\
import streamlit as st
import pandas as pd

# Load dynamic path
with open("config/data_path.txt") as f:
    path = f.read().strip()

df = pd.read_csv(path)

st.title("🚀 Transition Capital Dashboard")

st.metric("Total PnL", f"{df['pnl'].sum():,.0f}")
st.metric("Win Rate", f"{(df['pnl']>0).mean()*100:.2f}%")

df["equity"] = df["pnl"].cumsum()

st.line_chart(df["equity"])

st.scatter_chart(df[["signal_score", "pnl"]])
"""

open("dashboard.py", "w").write(content)

print("✅ Dashboard path fixed")