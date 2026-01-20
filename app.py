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


