import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders
import base64

# =============================
# AUTO-REFRESH EVERY 1 MINUTE
# =============================
count = st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

import streamlit as st

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Algo Trade", layout="wide")

# =============================
# HERO BACKGROUND IMAGE + SLOGAN
# =============================
hero_image_url = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=1920&q=80"

st.markdown(
    f"""
    <style>
    .hero {{
        background-image: url("{hero_image_url}");
        background-size: cover;
        background-position: center;
        height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: white;
        font-family: 'Arial', sans-serif;
    }}
    .hero h1 {{
        font-size: 60px;
        margin: 0;
        font-weight: bold;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    }}
    .hero p {{
        font-size: 28px;
        margin: 5px 0 0 0;
        text-shadow: 1px 1px 6px rgba(0,0,0,0.7);
    }}
    .brands {{
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }}
    .brands img {{
        margin: 0 15px;
        height: 50px;
        opacity: 0.8;
    }}
    </style>

    <div class="hero">
        <h1>Build Your System with</h1>
        <p>ALGO TRADE</p>
        <div class="brands">
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/4a/Logo_2013_Google.png" />
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/ab/Apple-logo.png" />
            <img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Microsoft_logo_%282012%29.svg" />
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================
# BELOW THIS YOU CAN PUT YOUR TRADING LOGIC
# =============================
st.title("📊 Trading Dashboard")
st.write("Your dashboard content goes here.")


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
