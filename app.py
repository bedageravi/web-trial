import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders
import pandas as pd
import base64

# =============================
# AUTO-REFRESH EVERY 1 MINUTE
# =============================
count = st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Algo Trade", layout="wide")

# =============================
# SET FULL SOLID PURPLE BACKGROUND
# =============================
def set_bg_color():
    st.markdown(
        """
        <style>
        /* Full page solid purple background */
        [data-testid="stAppViewContainer"] {
            background-color: #5D3FD3;  /* Solid purple */
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0.0);
        }
        [data-testid="stToolbar"] {
            right: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_color()

# =============================
# HERO TEXT
# =============================
st.markdown(
    """
    <div style="text-align:center; padding-top:120px; color:white; text-shadow: 2px 2px 6px rgba(0,0,0,0.7);">
        <h1 style="font-size:60px;">Build Your System with</h1>
        <h2 style="font-size:40px;">ALGO TRADE</h2>
    </div>
    """,
    unsafe_allow_html=True
)


})
st.dataframe(df_positions, width='stretch')

# =============================
# SESSION INIT
# =============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "manual_refresh" not in st.session_state:
    st.session_state.manual_refresh = 0

# =============================
# CHECK TOKEN
# =============================
auth_data = load_auth()
st.session_state.logged_in = auth_data is not None

# =============================
# LOGIN OR DASHBOARD FLOW
# =============================
if not st.session_state.logged_in:
    login_page()
else:
    st.success("✅ Logged in. Fetching data...")

    # -------------------------
    # MANUAL REFRESH BUTTON
    # -------------------------
    if st.button("🔄 Refresh Dashboard"):
        st.session_state.manual_refresh += 1  # triggers rerun automatically

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

    # -------------------------
    # LOGOUT
    # -------------------------
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
