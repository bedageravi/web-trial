import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

from login import login
from positions import positions
from orders import orders

st.set_page_config(page_title="Algo Demo Dashboard", layout="wide")

# =========================
# SESSION STATE INITIALIZATION
# =========================
if "login_msg" not in st.session_state:
    st.session_state.login_msg = None
if "positions_df" not in st.session_state:
    st.session_state.positions_df = None
if "orders_df" not in st.session_state:
    st.session_state.orders_df = None
if "strategy_results" not in st.session_state:
    st.session_state.strategy_results = []
if "planetary_positions" not in st.session_state:
    st.session_state.planetary_positions = []

IST = pytz.timezone("Asia/Kolkata")

# --- 🔄 REFRESH BUTTON ---
if st.button("🔄 Refresh Dashboard"):
    st.session_state.login_msg = None
    st.session_state.positions_df = None
    st.session_state.orders_df = None
    st.session_state.strategy_results = []
    st.session_state.planetary_positions = []

st.title("📊 Algo Demo Dashboard")
st.write("Manual Refresh Only (Click button to update)")

# --- 1️⃣ LOGIN BUTTON ---
st.subheader("1️⃣ Login")
mpin_input = st.text_input("Enter MPIN:", type="password")
login_clicked = st.button("Login to Kotak")

if login_clicked:
    if not mpin_input:
        st.warning("Please enter MPIN")
    else:
        success, msg = login.kotak_login(mpin_input)
        st.session_state.login_msg = msg
        if success:
            st.success(msg)
        else:
            st.error(msg)

if st.session_state.login_msg:
    st.info(f"Last Login Message: {st.session_state.login_msg}")

st.markdown("---")

# --- 2️⃣ POSITIONS BUTTON ---
st.subheader("2️⃣ Current Positions")
positions_clicked = st.button("Show Positions")

if positions_clicked:
    df_pos, msg = positions.get_positions()
    if df_pos is not None:
        st.session_state.positions_df = df_pos
    else:
        st.warning(msg)

if st.session_state.positions_df is not None:
    st.dataframe(st.session_state.positions_df)

st.markdown("---")

# --- 3️⃣ ORDERS BUTTON ---
st.subheader("3️⃣ Today's Orders")
orders_clicked = st.button("Show Orders")

if orders_clicked:
    df_ord, msg = orders.get_orders()
    if df_ord is not None:
        st.session_state.orders_df = df_ord
    else:
        st.warning(msg)

if st.session_state.orders_df is not None:
    st.dataframe(st.session_state.orders_df)

st.markdown("---")

# --- 4️⃣ SMA STRATEGY BUTTON ---
st.subheader("4️⃣ SMA Strategy")

symbol_input = st.text_input("Enter Stock Symbol (e.g. VEDL, IRFC):", value="WIPRO").upper()

interval = st.selectbox(
    "Select Timeframe",
    ["1m", "5m", "15m", "30m", "60m", "1d", "1wk"],
    index=1  # default 5m
)

sma_input = st.text_input(
    "Enter SMA periods (comma separated)",
    value="20,50,100"
)

# Convert SMA periods to list of integers
try:
    sma_periods = [int(x.strip()) for x in sma_input.split(",") if x.strip().isdigit()]
except:
    sma_periods = [20,50,100]

strategy_clicked = st.button("Run SMA Strategy")

if strategy_clicked:
    if not symbol_input:
        st.warning("Please enter a stock symbol")
    else:
        with st.spinner(f"Fetching {symbol_input} data for {interval} timeframe and calculating SMAs..."):
            try:
                from strategy.sma_strategy import run_stock_strategy
                results = run_stock_strategy(
                    symbol=symbol_input,
                    interval=interval,
                    sma_periods=sma_periods
                )
                if results:
                    st.session_state.strategy_results = [(symbol_input, results)]
                else:
                    st.warning(f"No data returned for {symbol_input} at {interval} timeframe")
            except Exception as e:
                st.error(f"Error running strategy: {e}")

# --- DISPLAY SMA RESULTS ---
for symbol, results in st.session_state.strategy_results:
    st.write(f"### 📌 {symbol} ({interval})")
    res = results[0]
    
    # Latest close and time from SMA strategy
    latest_close = res['latest_close']
    latest_time = res['datetime']  # already IST from strategy

    # Current actual time in IST (when script ran)
    current_time_ist = datetime.now(pytz.UTC).astimezone(IST).strftime("%Y-%m-%d %H:%M:%S %Z")

    st.write(f"Close Price: ₹{latest_close}")
    st.write(f"Candle Time: {latest_time}")           # last candle time
    st.write(f"Signal Checked At: {current_time_ist}")  # script run time
    st.write(f"Data Source: {res['data_source']}")

    # --- SMA Table ---
    table_data = []
    for p, info in res['smas'].items():
        val = info['value'] if info['value'] is not None else "Not available"
        dist = f"{info['distance']}%" if info['distance'] is not None else "-"
        touch = "TOUCH" if info['touch'] else ""
        table_data.append({
            "SMA": f"SMA{p}",
            "Value": val,
            "Distance %": dist,
            "Touch": touch
        })

    st.dataframe(pd.DataFrame(table_data))
