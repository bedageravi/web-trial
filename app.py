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

st.set_page_config(page_title="Algo Trade", layout="wide")

VIDEO_URL = "https://cdn.pixabay.com/video/2020/01/14/31251-385265625_large.mp4"

st.markdown(
    f"""
    <style>
    .video-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: -1;
    }}
    .overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        z-index: -1;
    }}
    .hero-text {{
        position: relative;
        text-align: center;
        color: white;
        padding-top: 120px;
        font-family: 'Arial', sans-serif;
    }}
    .hero-text h1 {{
        font-size: 64px;
        font-weight: bold;
    }}
    .hero-text p {{
        font-size: 32px;
    }}
    </style>

    <video autoplay muted loop class="video-bg">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>

    <div class="overlay"></div>

    <div class="hero-text">
        <h1>Build Your System with</h1>
        <p><strong>ALGO TRADE</strong></p>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================
# Your app content below
# =====================

st.title("📈 Trading Web App")
st.write("Your dashboard content starts here...")




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
