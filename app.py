import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders
import pandas as pd
import random

# =============================
# AUTO REFRESH
# =============================
st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="ALGO TRADE ™", layout="wide")

# =============================
# BLACK GRADIENT BACKGROUND
# =============================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #2b2b2b, #000000);
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0.0);
}

div.stButton > button:first-child {
    background-color: white;
    color: black;
    font-weight: bold;
    border-radius: 8px;
    height: 40px;
    width: 180px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# IMAGE LIST
# =============================
IMAGE_LIST = [
    "https://cdn.pixabay.com/photo/2020/06/11/19/40/bull-5284793_1280.jpg",
    "https://cdn.pixabay.com/photo/2017/03/30/15/10/stock-2187070_1280.jpg",
    "https://cdn.pixabay.com/photo/2018/05/02/12/42/bitcoin-3368467_1280.jpg"
]

selected_image = random.choice(IMAGE_LIST)

# =============================
# TOP IMAGE (MEDIUM SIZE)
# =============================
st.image(selected_image, width=900)

# =============================
# HERO TEXT
# =============================
st.markdown("""
<div style="text-align:center; color:white; padding-top:15px; padding-bottom:25px;">
    <h1 style="font-size:42px;">Build Your Automated Trading System</h1>
    <h2 style="font-size:30px;">ALGO TRADE ™</h2>
</div>
""", unsafe_allow_html=True)

# =============================
# SESSION INIT
# =============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "manual_refresh" not in st.session_state:
    st.session_state.manual_refresh = 0

# =============================
# AUTH CHECK
# =============================
auth_data = load_auth()
st.session_state.logged_in = auth_data is not None

# =============================
# LOGIN OR DASHBOARD
# =============================
if not st.session_state.logged_in:
    login_page()
else:
    st.success("✅ Logged in. Fetching data...")

    if st.button("🔄 Refresh Dashboard"):
        st.session_state.manual_refresh += 1

    # -------------------------
    # POSITIONS
    # -------------------------
    with st.spinner("Fetching Positions..."):
        df_positions, msg_pos = get_positions()
        if df_positions is not None:
            st.subheader("📊 MTF Positions")
            st.dataframe(df_positions, use_container_width=True)
        else:
            st.warning(msg_pos)

    # -------------------------
    # ORDERS
    # -------------------------
    with st.spinner("Fetching Orders..."):
        df_orders, msg_ord = get_orders()
        if df_orders is not None:
            st.subheader("🧾 Today's Orders")
            st.dataframe(df_orders, use_container_width=True)
        else:
            st.warning(msg_ord)

    st.divider()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
