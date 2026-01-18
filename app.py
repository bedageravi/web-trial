import streamlit as st
from streamlit_autorefresh import st_autorefresh
from login import login_page, load_auth
from positions import get_positions
from orders import get_orders

# =============================
# AUTO-REFRESH EVERY 30 SECONDS
# =============================
count = st_autorefresh(interval=30*1000, limit=None, key="auto_refresh")

st.set_page_config(page_title="Trading Web App", layout="wide")
st.title("📈 Trading Web App")

# -----------------------------
# BACKGROUND IMAGE (CSS)
# -----------------------------
page_bg_img = """
<style>
body {
background-image: url('https://images.unsplash.com/photo-1612392061780-d62c8b9bce36?auto=format&fit=crop&w=1950&q=80');
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# -----------------------------
# SESSION INIT
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "manual_refresh" not in st.session_state:
    st.session_state.manual_refresh = 0

# -----------------------------
# CHECK TOKEN
# -----------------------------
auth_data = load_auth()
if auth_data is None:
    st.session_state.logged_in = False
else:
    st.session_state.logged_in = True

# -----------------------------
# LOGIN OR DASHBOARD FLOW
# -----------------------------
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
    # TABS FOR POSITIONS & ORDERS
    # -------------------------
    tab1, tab2 = st.tabs(["📊 MTF Positions", "🧾 Today's Orders"])

    # -------------------------
    # POSITIONS TAB
    # -------------------------
    with tab1:
        with st.spinner("Fetching Positions..."):
            df_positions, msg_pos = get_positions()
            if df_positions is not None and not df_positions.empty:
                st.dataframe(df_positions, use_container_width=True)
            else:
                st.warning(msg_pos)

    # -------------------------
    # ORDERS TAB
    # -------------------------
    with tab2:
        with st.spinner("Fetching Orders..."):
            df_orders, msg_ord = get_orders()
            if df_orders is not None and not df_orders.empty:
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
