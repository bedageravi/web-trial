import streamlit as st
from login import login_page
from positions import get_positions
from orders import get_orders

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Trading Web App", layout="wide")
st.title("📈 Trading Web App")

# =============================
# SESSION INIT
# =============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =============================
# LOGIN FLOW
# =============================
if not st.session_state.logged_in:
    login_page()
    st.stop()  # stop execution until login is successful

# =============================
# DASHBOARD AFTER LOGIN
# =============================
st.success("✅ Login successful. Fetching data...")

# -----------------------------
# POSITIONS
# -----------------------------
with st.spinner("Fetching Positions..."):
    df_positions, msg_pos = get_positions()
    if df_positions is not None:
        st.subheader("📊 MTF Positions")
        st.dataframe(df_positions, use_container_width=True)
    else:
        st.warning(msg_pos)

# -----------------------------
# ORDERS
# -----------------------------
with st.spinner("Fetching Orders..."):
    df_orders, msg_ord = get_orders()
    if df_orders is not None:
        st.subheader("🧾 Today's Orders")
        st.dataframe(df_orders, use_container_width=True)
    else:
        st.warning(msg_ord)

st.divider()

# -----------------------------
# LOGOUT (Safe version)
# -----------------------------
if st.button("Logout"):
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    # Instead of experimental_rerun, just stop execution for now
    st.stop()
