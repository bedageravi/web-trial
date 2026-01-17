import streamlit as st
from login import login  # Import the login function

st.title("Minimal Login Test")

# Call login function
client = login()

if client:
    st.write("Neo client initialized successfully!")
else:
    st.write("Login failed or client not initialized.")
