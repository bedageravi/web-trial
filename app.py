import streamlit as st
from login import login_page

st.set_page_config(
    page_title="Trading Web App",
    layout="centered"
)

st.title("📈 Trading Web App")

# INIT SESSION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# SHOW LOGIN OR DASHBOARD
if not st.session_state.logged_in:
    login_page()
else:
    st.success("Welcome! Login successful 🎉")

    st.write("👉 Your strategy dashboard will come here")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
