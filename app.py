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
    st.stop()  # stop until login success

# =============================
# DASHBOARD
# =============================
st.success("Welcome! Login successful 🎉")

# =============================
# AUTO-LOAD POSITIONS
# =============================
with st.spinner("Fetching positions..."):
    df_pos, msg_pos = get_positions()
    if df_pos is not None:
        st.subheader("📊 Positions")
        st.dataframe(df_pos, use_container_width=True)
    else:
        st.warning(msg_pos)

# =============================
# AUTO-LOAD ORDERS
# =============================
with st.spinner("Fetching orders..."):
    df_ord, msg_ord = get_orders()
    if df_ord is not None:
        st.subheader("🧾 Orders")
        st.dataframe(df_ord, use_container_width=True)
    else:
        st.warning(msg_ord)

st.divider()

# ============================
# LOGOUT
# =============================
if st.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()
