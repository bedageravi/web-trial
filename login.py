import streamlit as st
import pyotp
import requests
from supabase import create_client, Client
import time

# =========================
# HARD-CODED SUPABASE CONFIG
# =========================
SUPABASE_URL = "https://kyaqnoyrwyrekygfarey.supabase.co"
SUPABASE_KEY = "sb_secret_WX_R_MMSvmU_-NQgsARXmw_v-l7EKNM"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# HARD-CODED KOTAK SECRETS
# =========================
ACCESS_TOKEN_SHORT = "your-access-token"
MOBILE = "+91xxxxxxxxxx"
UCC = "XXTBL"
TOTP_SECRET = "your-totp-secret"

# =========================
# GLOBAL HEADERS
# =========================
HEADERS = {"Auth": None, "Sid": None, "neo-fin-key": "neotradeapi", "accept": "application/json"}

# =========================
# LOGIN FUNCTION
# =========================
def kotak_login(mpin_input: str, user_id="default_user"):
    totp = pyotp.TOTP(TOTP_SECRET).now()
    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    # Step 1: login
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

    # Step 2: validate MPIN
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

    # =========================
    # SAVE TOKEN TO SUPABASE
    # =========================
    expires_at = int(time.time()) + 6*3600  # 6 hours
    record = {
        "user_id": user_id,
        "auth_token": auth_token,
        "sid": auth_sid,
        "base_url": base_url,
        "expires_at": expires_at
    }

    # Upsert token (insert or update existing)
    supabase.table("auth_tokens").upsert(record, on_conflict="user_id").execute()

    # Update global HEADERS
    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "Kotak login successful ✅"

# =========================
# LOAD AUTH FUNCTION
# =========================
def load_auth(user_id="default_user"):
    result = supabase.table("auth_tokens").select("*").eq("user_id", user_id).execute()
    data = result.data
    if data:
        record = data[0]
        if record["expires_at"] > int(time.time()):
            HEADERS["Auth"] = record["auth_token"]
            HEADERS["Sid"] = record["sid"]
            return record
    return None

# =========================
# STREAMLIT LOGIN PAGE
# =========================
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
