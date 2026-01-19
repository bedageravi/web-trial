import streamlit as st
import pyotp
import requests
from datetime import datetime, timezone
from supabase import create_client

# ------------------------
# STREAMLIT SECRETS
# ------------------------
ACCESS_TOKEN_SHORT = st.secrets["kotak"]["ACCESS_TOKEN_SHORT"]
MOBILE = st.secrets["kotak"]["mobile"]
UCC = st.secrets["kotak"]["ucc"]
TOTP_SECRET = st.secrets["kotak"]["totp_secret"]

SUPABASE_URL = st.secrets["kotak"]["url"]
SUPABASE_SERVICE_KEY = st.secrets["kotak"]["anon_key"]

# ------------------------
# SUPABASE CLIENT
# ------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ------------------------
# GLOBAL HEADERS
# ------------------------
HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

# ------------------------
# KOTAK LOGIN FUNCTION
# ------------------------
def kotak_login(mpin_input: str):
    """Perform Kotak Neo login and save session in Supabase"""
    
    totp_secret_clean = TOTP_SECRET.strip().replace(" ", "")
    totp = pyotp.TOTP(totp_secret_clean).now()

    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
