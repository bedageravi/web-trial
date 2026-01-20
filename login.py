import json
import pyotp
import requests
import time
from pathlib import Path
import streamlit as st

# ----------------------------
# AUTH FILE (root folder)
# ----------------------------
AUTH_FILE = Path("auth.json")

# ----------------------------
# Kotak credentials
# ----------------------------
try:
    ACCESS_TOKEN_SHORT = st.secrets["kotak"]["access_token"]
    MOBILE = st.secrets["kotak"]["mobile"]
    UCC = st.secrets["kotak"]["ucc"]
    TOTP_SECRET = st.secrets["kotak"]["totp_secret"]
except KeyError:
    st.error("Kotak secrets missing! Add them in Streamlit Secrets.")
    st.stop()

HEADERS = {"Auth": None, "Sid": None, "neo-fin-key": "neotradeapi", "accept": "application/json"}

# ----------------------------
# Logout function
# ----------------------------
def logout():
    """Clear auth.json and session"""
    if AUTH_FILE.exists():
        AUTH_FILE.unlink()
    st.session_state.logged_in = False
    st.session_state.login_msg = ""
    st.success("Logged out successfully. Please login again.")

# ----------------------------
# Step1 + Step2 login
# ----------------------------
def kotak_login(mpin_input: str, token_validity_hours: int = 12):
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
        return False, f"Step1 error: {e}"

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
    with open(AUTH_FILE, "w") as f:
        json.dump({
            "AUTH_TOKEN": auth_token,
            "AUTH_SID": auth_sid,
            "BASE_URL": base_url,
            "EXPIRES_AT": time.time() + token_validity_hours * 3600
        }, f, indent=2)

    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "✅ Login successful"

# ----------------------------
# Load auth.json safely
# ----------------------------
def load_auth():
    try:
        if AUTH_FILE.exists():
            with open(AUTH_FILE, "r") as f:
                data = json.load(f)
            if data.get("EXPIRES_AT", 0) > time.time():
                HEADERS["Auth"] = data["AUTH_TOKEN"]
                HEADERS["Sid"] = data["AUTH_SID"]
                return data
        return None
    except Exception as e:
        st.warning(f"Error reading auth.json: {e}")
        return None

# ----------------------------
# Headers for API
# ----------------------------
def get_auth_headers():
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
    if "login_cycle" not in st.session_state:
        st.session_state.login_cycle = 0
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "login_msg" not in st.session_state:
        st.session_state.login_msg = ""

    # 1️⃣ Try old auth first
    auth_data = load_auth()
    if auth_data and st.session_state.login_cycle == 0:
        st.session_state.logged_in = True
        st.success("✅ Logged in using previous auth")
        st.session_state.login_cycle += 1
        return

    # 2️⃣ Fresh login
    mpin = st.text_input("Enter MPIN", type="password")
    if st.button("Login"):
        with st.spinner("Logging in..."):
            success, msg = kotak_login(mpin)
            st.session_state.login_msg = msg
            if success:
                st.session_state.logged_in = True
            else:
                st.session_state.login_cycle += 1
                if st.session_state.login_cycle >= 2:
                    st.warning("Old auth failed. Please login fresh with MPIN.")
                    st.session_state.login_cycle = 0

    # Display message & logout button
    if st.session_state.logged_in:
        st.success(st.session_state.login_msg)
        if st.button("Logout"):
            logout()
    elif st.session_state.login_msg:
        st.error(st.session_state.login_msg)
