import streamlit as st
from login import login_page

st.set_page_config(page_title="Trading App Demo", layout="centered")

st.title("📈 Trading Web App")

# Call login page
login_page()

# After login (demo condition)
if st.session_state.get("logged_in", False):
    st.success("Welcome! Login successful 🎉")
    st.write("👉 Your strategy dashboard will come here")
