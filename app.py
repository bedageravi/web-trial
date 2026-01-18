import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders

# =============================
# AUTO-REFRESH
# =============================
count = st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Algo Trade", layout="wide")

# =============================
# BACKGROUND: BLACK + TOP IMAGE HERO
# =============================
hero_image_url = "https://cdn.pixabay.com/photo/2020/06/11/19/40/bull-5284793_1280.jpg"

st.markdown(
    f"""
    <style>
    /* ENTIRE PAGE BLACK BACKGROUND */
    [data-testid="stAppViewContainer"] {{
        background-color: black;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: rgba(0,0,0,0.0);
    }}

    /* TOP HERO IMAGE */
    .top-hero {{
        background-image: url("{hero_image_url}");
        background-size: cover;
        background-position: center;
        height: 50vh;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        font-family: Arial, sans-serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    }}
    .top-hero h1 {{
        font-size: 60px;
        margin: 0;
    }}
    .top-hero p {{
        font-size: 36px;
        margin: 5px 0 0 0;
    }}
    </style>

    <div class="top-hero">
        <div>
            <h1>Build Your System with</h1>
            <p><strong>ALGO TRADE</strong></p>
        </div>
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
# CHECK TOKEN
# =============================
auth_data = load_auth()
if auth_data is None:
    st.session_state.logged_in = False
else:
    st.session_state.logged_in = True

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
            st.dataframe(df_positions, width='stretch')  # updated
        else:
            st.warning(msg_pos)

    # -------------------------
    # ORDERS
    # -------------------------
    with st.spinner("Fetching Orders..."):
        df_orders, msg_ord = get_orders()
        if df_orders is not None:
            st.subheader("🧾 Today's Orders")
            st.dataframe(df_orders, width='stretch')  # updated
        else:
            st.warning(msg_ord)

    st.divider()

    # -------------------------
    # LOGOUT
    # -------------------------
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
