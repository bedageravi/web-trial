import streamlit as st

def login_page():
    st.subheader("🔐 Login")

    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # DEMO logic only
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")
