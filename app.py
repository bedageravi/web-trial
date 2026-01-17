import streamlit as st
from login import kotak_login, load_auth

st.title("Kotak Login Test")

mpin = st.text_input("Enter MPIN", type="password")

if st.button("Login"):
    success, message = kotak_login(mpin)
    if success:
        st.success(message)
        auth_data = load_auth()
        st.json(auth_data)
    else:
        st.error(message)
