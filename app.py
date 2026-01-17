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
