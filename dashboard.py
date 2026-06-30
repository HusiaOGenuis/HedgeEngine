import streamlit as st
import pandas as pd
import time

from core.execution.mt5_live_real import connect_mt5, get_account, get_positions

st.set_page_config(layout="wide")

# ✅ CONNECT
connected = connect_mt5()

# ✅ CONTROLS
st.sidebar.header("⚙️ Control Panel")

risk_per_trade = st.sidebar.slider("Risk per Trade (%)", 0.1, 1.0, 0.5) / 100
max_exposure = st.sidebar.slider("Max Portfolio Exposure (%)", 1, 10, 3) / 100
reserve_ratio = st.sidebar.slider("Capital Reserve (%)", 20, 70, 40) / 100

# ✅ HEADER
st.title("🚀 HedgeEngine Live Cockpit")

# ✅ ACCOUNT PANEL (REAL)
st.subheader("💰 Live Account")

if not connected:
    st.error("MT5 NOT CONNECTED")
else:
    acc = get_account()

    if acc:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Balance", f"{acc['balance']:.2f}")
        col2.metric("Equity", f"{acc['equity']:.2f}")
        col3.metric("Margin", f"{acc['margin']:.2f}")
        col4.metric("Free Margin", f"{acc['free_margin']:.2f}")
    else:
        st.write("No account data")

# ✅ POSITIONS PANEL (REAL)
st.subheader("📡 Open Positions")

positions = get_positions()

if positions:
    df = pd.DataFrame(positions)
    st.dataframe(df)
else:
    st.write("No open positions")

# ✅ CONTEXT PANEL
st.subheader("🧠 Control Interpretation")

st.write("Risk per Trade:", risk_per_trade)
st.write("Max Exposure:", max_exposure)
st.write("Reserve Ratio:", reserve_ratio)

# ✅ AUTO REFRESH
time.sleep(2)
st.rerun()
