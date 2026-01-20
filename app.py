import streamlit as st
import pandas as pd
import yfinance as yf

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

# --- 🔄 REFRESH BUTTON (NEW METHOD) ---
if st.button("🔄 Refresh Dashboard"):
    # Clear all session state data
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

# --- 4️⃣ DEMO STRATEGY BUTTON ---
st.subheader("4️⃣ Stock Info & Sun–Mercury Strategy")
symbol_input = st.text_input("Enter Stock Symbol (e.g. VEDL, IRFC):").upper()
strategy_clicked = st.button("Run Stock Info & Strategy")

if strategy_clicked:
    if not symbol_input:
        st.warning("Please enter a stock symbol")
    else:
        with st.spinner(f"Fetching data for {symbol_input} and running strategy..."):
            try:
                from strategy.sun_mercury import run_stock_strategy
                results = run_stock_strategy(symbol_input)
                if results:
                    st.session_state.strategy_results.append((symbol_input, results))
                else:
                    st.warning(f"No results found for {symbol_input}")
            except Exception as e:
                st.error(f"Error running strategy: {e}")

for symbol, results in st.session_state.strategy_results:
    st.write(f"### 📌 {symbol} Strategy Results")
    latest_close = results[0]["latest_close"]
    st.write(f"Latest Close: ₹{latest_close}")

    table_data = []
    for r in results[:10]:
        if r["price"]:
            table_data.append({
                "Aspect": r["aspect_name"],
                "Aspect Date": r["aspect_date"],
                "Past Close": r["price"]["close"],
                "Open": r["price"]["open"],
                "High": r["price"]["high"],
                "Low": r["price"]["low"],
                "% Change vs Latest": r["pct_change"]
            })
        else:
            table_data.append({
                "Aspect": r["aspect_name"],
                "Aspect Date": r["aspect_date"],
                "Past Close": "N/A",
                "Open": "N/A",
                "High": "N/A",
                "Low": "N/A",
                "% Change vs Latest": "N/A"
            })
    st.dataframe(pd.DataFrame(table_data))

st.markdown("---")

# --- 5️⃣ PLANETARY POSITIONS BUTTON ---
st.subheader("5️⃣ Planetary Positions")
planetary_clicked = st.button("Get Planetary Positions")

if planetary_clicked:
    try:
        from planet_positions.planet_positions import get_planet_positions
        positions_list = get_planet_positions()
        st.session_state.planetary_positions.extend(positions_list)
    except Exception as e:
        st.error(f"Error fetching planetary positions: {e}")

for p in st.session_state.planetary_positions:
    st.write(p)
