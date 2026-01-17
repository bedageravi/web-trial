import streamlit as st
from login import login_page
from positions import get_positions
from orders import get_orders

st.set_page_config(page_title="Trading Web App", layout="wide")
st.title("📈 Trading Web App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# LOGIN
if not st.session_state.logged_in:
    login_page()
    st.stop()  # stop until login success

# DASHBOARD
st.success("Welcome! Login successful 🎉")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Load Positions"):
        with st.spinner("Fetching positions..."):
            df, msg = get_positions()
            if df is not None:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning(msg)

with col2:
    if st.button("🧾 Load Orders"):
        with st.spinner("Fetching orders..."):
            df, msg = get_orders()
            if df is not None:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning(msg)

st.divider()

if st.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()
