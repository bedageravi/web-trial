import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders
from pathlib import Path
import pandas as pd
import random

# =============================
# AUTO REFRESH (100 sec)
# =============================
st_autorefresh(interval=100 * 1000, limit=None, key="auto_refresh")

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
h1, h2, h3, h4, h5 {
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =============================
# HERO TEXT
# =============================
st.markdown("""
<div style="text-align:center; color:white;">
    <h1 style="font-size:38px;">Build Your Emotional Discipline</h1>
    <h3 style="font-size:30px;">With Our Automated Trading System</h3>
</div>
""", unsafe_allow_html=True)

# =============================
# RANDOM HERO IMAGE
# =============================
IMAGE_LIST = [
    "https://images.pexels.com/photos/6770775/pexels-photo-6770775.jpeg",
    "https://wallpapercave.com/wp/wp9587572.jpg",
    "https://images.pexels.com/photos/5834234/pexels-photo-5834234.jpeg"
]

if "bg_image" not in st.session_state:
    st.session_state.bg_image = random.choice(IMAGE_LIST)

st.markdown(
    f"""
    <div style="display:flex; justify-content:center; padding:10px;">
        <img src="{st.session_state.bg_image}" style="width:500px; height:500px;" />
    </div>
    """,
    unsafe_allow_html=True
)

# =============================
# SUBHEADING
# =============================
st.markdown("""
<div style="text-align:center; color:white; padding-bottom:25px;">
    <h2 style="font-size:30px;">KOTAK ALGO TRADE ™</h2>
</div>
""", unsafe_allow_html=True)

# =============================
# AUTH CHECK (auth.json = truth)
# =============================
auth_data = load_auth()

if not auth_data:
    login_page()
    st.stop()   # ⛔ stop app until login

st.success("✅ Logged in. Fetching data...")

# =============================
# MANUAL REFRESH
# =============================
if "manual_refresh" not in st.session_state:
    st.session_state.manual_refresh = 0

if st.button("🔄 Refresh Dashboard"):
    st.session_state.manual_refresh += 1

# =============================
# POSITIONS
# =============================
with st.spinner("Fetching Positions..."):
    result = get_positions()

    if isinstance(result, tuple) and isinstance(result[0], pd.DataFrame):
        df_positions, summary = result

        st.markdown('<h3>📊 MTF Positions</h3>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.markdown(f"<h4>Overall P&L (₹): {summary['total_pnl']}</h4>", unsafe_allow_html=True)
        col2.markdown(f"<h4>Overall Return %: {summary['total_pct']}</h4>", unsafe_allow_html=True)

        styled_df = df_positions.style.map(lambda _: 'color: black')
        st.dataframe(styled_df, use_container_width=True)

    else:
        st.warning(result[1] if result else "No positions found")

# =============================
# ORDERS
# =============================
with st.spinner("Fetching Orders..."):
    df_orders, msg = get_orders()

    if df_orders is not None and not df_orders.empty:
        st.markdown('<h3>🧾 Today\'s Orders</h3>', unsafe_allow_html=True)
        styled_orders = df_orders.style.map(lambda _: 'color: black')
        st.dataframe(styled_orders, use_container_width=True)
    else:
        st.warning(msg)

st.divider()

# =============================
# LOGOUT
# =============================
AUTH_FILE = Path("auth.json")

if st.button("Logout"):
    if AUTH_FILE.exists():
        AUTH_FILE.unlink()
    st.success("Logged out successfully!")
    st.rerun()
