import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders
import pandas as pd

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Algo Trade", layout="wide")

# =============================
# AUTO-REFRESH EVERY 1 MINUTE
# =============================
st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

# =============================
# BACKGROUND IMAGE + DARK OVERLAY
# =============================
def set_bg_image(image_url):
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            position: relative;
        }}
        /* Dark overlay */
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(0,0,0,0.6);
            z-index: 0;
        }}
        [data-testid="stAppViewContainer"] > .main {{
            position: relative;
            z-index: 1;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0.0);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set a professional trading background image
set_bg_image("https://cdn.pixabay.com/photo/2020/06/11/19/40/bull-5284793_1280.jpg")

# =============================
# HERO SECTION
# =============================
st.markdown(
    """
    <div style="
        text-align:center; padding:100px 20px 50px 20px; 
        color:white; text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
        font-family: 'Arial', sans-serif;
        ">
        <h1 style="font-size:60px; margin-bottom:0;">ALGO TRADE</h1>
        <p style="font-size:28px; margin-top:5px;">Build your automated trading system</p>
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
    # FETCH DATA
    # -------------------------
    with st.spinner("Fetching Positions..."):
        df_positions, msg_pos = get_positions()
    with st.spinner("Fetching Orders..."):
        df_orders, msg_ord = get_orders()

    # -------------------------
    # LAYOUT: POSITIONS + ORDERS SIDE BY SIDE
    # -------------------------
    col1, col2 = st.columns(2)

    # Highlight PnL
    def highlight_pnl(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}; font-weight:bold'

    with col1:
        st.subheader("📊 MTF Positions")
        if df_positions is not None:
            st.dataframe(df_positions.style.applymap(highlight_pnl, subset=['PnL']),
                         use_container_width=True)
        else:
            st.warning(msg_pos)

    with col2:
        st.subheader("🧾 Today's Orders")
        if df_orders is not None:
            st.dataframe(df_orders, use_container_width=True)
        else:
            st.warning(msg_ord)

    st.divider()

    # -------------------------
    # LOGOUT BUTTON
    # -------------------------
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
