import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth, logout
from positions import get_positions
from orders import get_orders
import random

# ==================================================
# PAGE CONFIG (MUST BE FIRST)
# ==================================================
st.set_page_config(
    page_title="ALGO TRADE ™",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# AUTO REFRESH (SAFE)
# ==================================================
st_autorefresh(interval=60 * 1000, limit=None, key="auto_refresh")

# ==================================================
# SESSION INIT
# ==================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==================================================
# CHECK AUTH FROM SUPABASE
# ==================================================
auth_data = load_auth()
if auth_data:
    st.session_state.logged_in = True
else:
    st.session_state.logged_in = False

# ==================================================
# STYLE / BACKGROUND
# ==================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #2b2b2b, #000000);
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0.0);
}
div.stButton > button {
    background-color: white;
    color: black;
    font-weight: bold;
    border-radius: 8px;
    height: 42px;
    width: 200px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HERO IMAGE
# ==================================================
IMAGE_LIST = [
    "https://images.pexels.com/photos/6770775/pexels-photo-6770775.jpeg",
    "https://wallpapercave.com/wp/wp9587572.jpg",
    "https://images.pexels.com/photos/5834234/pexels-photo-5834234.jpeg"
]

selected_image = random.choice(IMAGE_LIST)

st.markdown(
    f"""
    <div style="display:flex; justify-content:center; padding-top:20px;">
        <img src="{selected_image}" style="width:420px; height:420px; border-radius:12px;" />
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<div style="text-align:center; color:white; padding-top:10px; padding-bottom:25px;">
    <h1 style="font-size:42px;">Build Your Automated Trading System</h1>
    <h2 style="font-size:28px;">ALGO TRADE ™</h2>
</div>
""", unsafe_allow_html=True)

# ==================================================
# LOGIN OR DASHBOARD
# ==================================================
if not st.session_state.logged_in:
    login_page()

else:
    st.success("✅ Logged in successfully")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()

    with col2:
        if st.button("🚪 Logout"):
            logout()
            st.rerun()

    st.divider()

    # ==================================================
    # POSITIONS
    # ==================================================
    with st.spinner("Fetching MTF Positions..."):
        df_pos, pos_msg = get_positions()

        if df_pos is not None and not df_pos.empty:
            st.subheader("📊 MTF Positions")
            st.dataframe(df_pos, use_container_width=True)
        else:
            st.warning(pos_msg)

    st.divider()

    # ==================================================
    # ORDERS
    # ==================================================
    with st.spinner("Fetching Today's Orders..."):
        df_ord, ord_msg = get_orders()

        if df_ord is not None and not df_ord.empty:
            st.subheader("🧾 Today's Orders")
            st.dataframe(df_ord, use_container_width=True)
        else:
            st.warning(ord_msg)
