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
st_autorefresh(interval=60_000, limit=None, key="auto_refresh")

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
    <div style="display:flex; justify-content:center; padding-top:20px;">
        <img src="{st.session_state.bg_image}" style="width:500px; height:500px;" />
    </div>
    """,
    unsafe_allow_html=True
)

# =============================
# HERO TEXT
# =============================
st.markdown("""
<div style="text-align:center; color:white; padding-top:10px; padding-bottom:25px;">
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
    # POSITIONS (WITH LTP + P&L)
    # -------------------------
    with st.spinner("Fetching Positions..."):
        result = get_positions()

        if isinstance(result, tuple) and isinstance(result[0], pd.DataFrame):
            df_positions, summary = result

            # Section Header
            st.markdown('<h3 style="color:white; font-weight:bold;">📊 MTF Positions</h3>', unsafe_allow_html=True)

            # Overall P&L metrics
            col1, col2 = st.columns(2)
            col1.markdown(f'<h4 style="color:white; font-weight:bold;">Overall P&L (₹): {summary["total_pnl"]}</h4>', unsafe_allow_html=True)
            col2.markdown(f'<h4 style="color:white; font-weight:bold;">Overall Return %: {summary["total_pct"]}</h4>', unsafe_allow_html=True)

            # -------------------------
            # COLOR FORMATTING
            # -------------------------
            def color_pnl(val):
                if val > 0:
                    return 'color: green; font-weight:bold'
                elif val < 0:
                    return 'color: red; font-weight:bold'
                else:
                    return 'color: white'

            # Symbol column black, numeric columns white, P&L colored
            styled_df = df_positions.style.applymap(color_pnl, subset=["P&L (₹)", "% Return"]) \
                                           .applymap(lambda x: 'color: black', subset=["Symbol"]) \
                                           .applymap(lambda x: 'color: black', subset=["Qty","AvgPrice","LTP"])

            # Display table with auto height, only actual rows
            st.dataframe(styled_df, width='stretch', height='auto')

        else:
            st.warning(result[1] if result else "No positions found")

    # -------------------------
    # ORDERS
    # -------------------------
    with st.spinner("Fetching Orders..."):
        df_orders, msg_ord = get_orders()
        if df_orders is not None and not df_orders.empty:
            st.markdown('<h3 style="color:white; font-weight:bold;">🧾 Today\'s Orders</h3>', unsafe_allow_html=True)
            st.dataframe(df_orders, width='stretch', height='auto')
        else:
            st.warning(msg_ord)

    st.divider()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
