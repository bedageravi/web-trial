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

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Trading Web App", layout="wide")

# =============================
# BLACK BACKGROUND FUNCTION
# =============================
def set_black_background():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =============================
# APPLY BLACK BACKGROUND
# =============================
set_black_background()

# =============================
# APP TITLE
# =============================
st.title("📈 Trading Web App")

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
