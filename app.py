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
# BACKGROUND STYLE
# =============================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #5D3FD3, #1b1b1b);
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
# HERO TEXT (TOP)
# =============================
st.markdown("""
<div style="text-align:center; color:black; padding-top:20px;">
    <h1 style="font-size:48px;">Build Your Automated Trading System</h1>
    <h2 style="font-size:32px;">ALGO TRADE ™</h2>
</div>
""", unsafe_allow_html=True)

# =============================
# ONLY ONE IMAGE (BELOW HERO)
# =============================
IMAGE_LIST = [
    "https://images.pexels.com/photos/23439083/pexels-photo-23439083.jpeg",
    "https://images.pexels.com/photos/6770775/pexels-photo-6770775.jpeg",
    "https://images.pexels.com/photos/5834234/pexels-photo-5834234.jpeg"
]

selected_image = random.choice(IMAGE_LIST)

st.image(selected_image, use_container_width=True)

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
