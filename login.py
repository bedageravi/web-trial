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
    }

    # Step 1: tradeApiLogin
    try:
        r1 = requests.post(
            "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin",
            headers=headers,
            json={"mobileNumber": MOBILE, "ucc": UCC, "totp": totp},
            timeout=10
        )
        data1 = r1.json().get("data", {})
        view_token = data1.get("token")
        view_sid = data1.get("sid")
    except Exception as e:
        return False, f"Step1 failed: {e}"

    if not view_token or not view_sid:
        return False, "Step1 failed: Invalid response"

    # Step 2: tradeApiValidate
    headers2 = headers.copy()
    headers2["sid"] = view_sid
    headers2["Auth"] = view_token

    try:
        r2 = requests.post(
            "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate",
            headers=headers2,
            json={"mpin": mpin_input},
            timeout=10
        )
        data2 = r2.json().get("data", {})
        auth_token = data2.get("token")
        auth_sid = data2.get("sid")
        base_url = data2.get("baseUrl")
    except Exception as e:
        return False, f"Step2 failed: {e}"

    if not auth_token or not auth_sid:
        return False, "Step2 failed: Invalid response"

    # ------------------------
    # SAVE SESSION TO SUPABASE
    # ------------------------
    record = {
        "auth_token": auth_token,
        "auth_sid": auth_sid,
        "base_url": base_url,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    supabase.table("auth_sessions").insert(record).execute()

    # Update global headers
    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "Kotak login successful ✅"

# ------------------------
# LOAD AUTH FROM SUPABASE
# ------------------------
def load_auth():
    """Fetch latest session from Supabase"""
    result = (
        supabase
        .table("auth_sessions")
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if result.data:
        record = result.data[0]
        HEADERS["Auth"] = record["auth_token"]
        HEADERS["Sid"] = record["auth_sid"]
        return record

    return None

# ------------------------
# STREAMLIT LOGIN PAGE
# ------------------------
def login_page():
    st.subheader("🔐 Kotak Neo Login")

    mpin = st.text_input("Enter MPIN", type="password")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "login_success" not in st.session_state:
        st.session_state.login_success = False
    if "login_msg" not in st.session_state:
        st.session_state.login_msg = ""

    if st.button("Login"):
        with st.spinner("Logging in..."):
            success, msg = kotak_login(mpin)
            st.session_state.login_success = success
            st.session_state.login_msg = msg
            if success:
                st.session_state.logged_in = True

    # Show messages
    if st.session_state.login_success:
        st.success(st.session_state.login_msg)
    elif st.session_state.login_msg:
        st.error(st.session_state.login_msg)
