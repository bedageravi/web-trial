import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders
import pandas as pd

# =============================
# AUTO-REFRESH EVERY 1 MINUTE
# =============================
count = st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Algo Trade ™", layout="wide")

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
# TRADEMARK HEADER (LOGO + NAME)
# =============================
st.markdown(
    """
    <style>
    .header-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 20px;
        background-color: rgba(0,0,0,0.2);
        border-radius: 10px;
        width: fit-content;
        margin-bottom: 20px;
    }
    .header-logo img {
        width: 50px;
        height: 50px;
        border-radius: 50%;
    }
    .header-logo h2 {
        color: white;
        margin: 0;
        font-family: 'Arial', sans-serif;
    }
    </style>
    <div class="header-logo">
        <img src="https://cdn.pixabay.com/photo/2020/06/11/19/40/bull-5284793_1280.jpg" />
        <h2>ALGO TRADE ™</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================
# HERO SECTION
# =============================
st.markdown(
    """
    <div style="text-align:center; padding-top:20px; padding-bottom:40px; color:white; text-shadow: 2px 2px 6px rgba(0,0,0,0.7);">
        <h1 style="font-size:60px; margin-bottom:0;">Build Your System with</h1>
        <h2 style="font-size:40px;">ALGO TRADE ™</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================
# SESSION INIT
# =============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "manual_refresh" not in st.session_state:
    st.session_state.manual_refresh = 0

# =============================
# CHECK AUTH
# =============================
auth_data = load_auth()
st.session_state.logged_in = auth_data is not None

# =============================
# GLASS CARD FUNCTION FOR TABLES
# =============================
def glass_card(title, df):
    st.markdown(
        f"""
        <div style="
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: white;
        ">
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.dataframe(df, use_container_width=True)

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
    # FETCH POSITIONS
    # -------------------------
    with st.spinner("Fetching Positions..."):
        df_positions, msg_pos = get_positions()
        if df_positions is not None:
            glass_card("📊 MTF Positions", df_positions)
        else:
            st.warning(msg_pos)

    # -------------------------
    # FETCH ORDERS
    # -------------------------
    with st.spinner("Fetching Orders..."):
        df_orders, msg_ord = get_orders()
        if df_orders is not None:
            glass_card("🧾 Today's Orders", df_orders)
        else:
            st.warning(msg_ord)

    st.divider()

    # -------------------------
    # LOGOUT BUTTON
    # -------------------------
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
