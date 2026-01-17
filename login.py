# login.py
from neo_api_client import NeoApiClient
import pyotp
import streamlit as st

# ------------------------------
# Configuration (replace with real credentials)
# ------------------------------
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
UCC = "YOUR_UCC"

# Optional: 2FA secret if using TOTP
TOTP_SECRET = "YOUR_TOTP_SECRET"

# ------------------------------
# Login function
# ------------------------------
def login():
    st.write("Initializing Neo login...")

    # Generate TOTP if needed
    if TOTP_SECRET:
        totp = pyotp.TOTP(TOTP_SECRET)
        otp = totp.now()
        st.write(f"Generated OTP: {otp}")  # You can remove in production
    else:
        otp = None

    # Initialize Neo API client
    client = NeoApiClient(
        access_token=ACCESS_TOKEN,
        ucc=UCC,
    )

    # Test login (placeholder)
    try:
        st.write("Logging in...")
        # Example: fetch user profile to test
        # profile = client.get_profile()   # Uncomment if Neo SDK supports
        st.success("Login function ready!")
        return client
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None
