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
# AUTO-REFRESH
# =============================
st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

# =============================
# BACKGROUND + DARK OVERLAY STABLE
# =============================
def set_bg_image(image_url):
    st.markdown(
        f"""
        <style>
        /* Main page background image */
        body {{
            background-image: url('{image_url}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Dark semi-transparent overlay for all Streamlit content */
        .stApp {{
            background-color: rgba(0,0,0,0.6);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Example professional image
set_bg_image("https://cdn.pixabay.com/photo/2021/06/09/17/07/technology-6325963_1280.jpg")

# =============================
# HERO SECTION
# =============================
st.markdown(
    """
    <div style="
        text-align:center; padding:80px 20px 40px 20px; 
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

    # Manual refresh
    if st.button("🔄 Refresh Dashboard"):
        st.session_state.manual_refresh += 1

    # Fetch data
    df_positions, msg_pos = get_positions()
    df_orders, msg_ord = get_orders()

    # Layout: Positions + Orders
    col1, col2 = st.columns(2)

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

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
