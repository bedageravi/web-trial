import streamlit as st
from login import login_page
from positions import get_positions

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Trading Web App",
    layout="wide"
)

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
    st.stop()

# =============================
# DASHBOARD
# =============================
st.success("Welcome! Login successful 🎉")

if st.button("📊 Load Positions"):
    with st.spinner("Fetching positions..."):
        df, msg = get_positions()
        if df is not None:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(msg)

st.divider()

# =============================
# LOGOUT
# =============================
if st.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()
