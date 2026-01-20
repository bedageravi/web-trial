import json
import pyotp
import requests
import time
from pathlib import Path
import streamlit as st

# ----------------------------
# AUTH FILE
# ----------------------------
AUTH_FILE = Path("login/auth.json")  # save token here

# ----------------------------
# Kotak credentials
# Move to Streamlit Secrets for security
# ----------------------------
try:
    ACCESS_TOKEN_SHORT = st.secrets["kotak"]["access_token"]
    MOBILE = st.secrets["kotak"]["mobile"]
    UCC = st.secrets["kotak"]["ucc"]
    TOTP_SECRET = st.secrets["kotak"]["totp_secret"]
except KeyError:
    st.error("Kotak secrets missing! Add them in Streamlit Secrets.")
    st.stop()

# ----------------------------
# Default headers
# ----------------------------
HEADERS = {"Auth": None, "Sid": None, "neo-fin-key": "neotradeapi", "accept": "application/json"}

# ----------------------------
# Perform Kotak login
# ----------------------------
def kotak_login(mpin_input: str, token_validity_hours: int = 12):
    """
    Perform Kotak login (Step1 + Step2) and save auth.json
    token_validity_hours: how long token should be valid
    """
    totp = pyotp.TOTP(TOTP_SECRET).now()
    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    # --- STEP 1 ---
    try:
        r1 = requests.post(
            "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin",
            headers=headers,
            json={"mobileNumber": MOBILE, "ucc": UCC, "totp": totp},
            timeout=10
        )
        r1.raise_for_status()
        data1 = r1.json().get("data", {})
        view_token = data1.get("token")
        view_sid = data1.get("sid")
        if not view_token or not view_sid:
            return False, f"Step1 login failed: {r1.json().get('error', 'Unknown error')}"
    except Exception as e:
        return False, f"Step1 login error: {e}"

    # --- STEP 2 ---
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
        r2.raise_for_status()
        data2 = r2.json().get("data", {})
        auth_token = data2.get("token")
        auth_sid = data2.get("sid")
        base_url = data2.get("baseUrl")

        if not auth_token or not auth_sid:
            return False, f"Step2 validate failed: {r2.json().get('error', 'Unknown error')}"

    except Exception as e:
        return False, f"Step2 error: {e}"

    # --- SAVE AUTH ---
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump({
            "AUTH_TOKEN": auth_token,
            "AUTH_SID": auth_sid,
            "BASE_URL": base_url,
            "EXPIRES_AT": time.time() + token_validity_hours * 3600  # token expiry
        }, f, indent=2)

    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "✅ Login successful"

# ----------------------------
# Load existing auth
# ----------------------------
def load_auth():
    """Load auth.json if exists and not expired"""
    if AUTH_FILE.exists():
        with open(AUTH_FILE, "r") as f:
            data = json.load(f)
        if data.get("EXPIRES_AT", 0) > time.time():
            HEADERS["Auth"] = data["AUTH_TOKEN"]
            HEADERS["Sid"] = data["AUTH_SID"]
            return data
    return None

# ----------------------------
# Get headers for API calls
# ----------------------------
def get_auth_headers():
    """Return HEADERS dict for API requests"""
    data = load_auth()
    if not data:
        return None
    return {
        "Auth": data["AUTH_TOKEN"],
        "Sid": data["AUTH_SID"],
        "neo-fin-key": "neotradeapi",
        "accept": "application/json"
    }

# ----------------------------
# Streamlit login page
# ----------------------------
def login_page():
    st.subheader("🔐 Kotak Neo Login")
    mpin = st.text_input("Enter MPIN", type="password")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "login_msg" not in st.session_state:
        st.session_state.login_msg = ""

    if st.button("Login"):
        with st.spinner("Logging in..."):
            success, msg = kotak_login(mpin)
            st.session_state.login_msg = msg
            if success:
                st.session_state.logged_in = True

    # Display message
    if st.session_state.logged_in:
        st.success(st.session_state.login_msg)
    elif st.session_state.login_msg:
        st.error(st.session_state.login_msg)
