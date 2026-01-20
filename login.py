import json
import pyotp
import requests
import streamlit as st
from pathlib import Path
import time

# =========================
# AUTH FILE
# =========================
AUTH_FILE = Path("auth.json")

# =========================
# LOAD SECRETS
# =========================
ACCESS_TOKEN_SHORT = st.secrets["kotak"]["access_token"]
MOBILE = st.secrets["kotak"]["mobile"]
UCC = st.secrets["kotak"]["ucc"]
TOTP_SECRET = st.secrets["kotak"]["totp_secret"]

# =========================
# BASE HEADERS
# =========================
BASE_HEADERS = {
    "neo-fin-key": "neotradeapi",
    "accept": "application/json",
    "Content-Type": "application/json"
}

# =========================
# KOTAK LOGIN
# =========================
def kotak_login(mpin: str):
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()

        # ---- STEP 1 ----
        r1 = requests.post(
            "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin",
            headers={
                **BASE_HEADERS,
                "Authorization": ACCESS_TOKEN_SHORT
            },
            json={
                "mobileNumber": MOBILE,
                "ucc": UCC,
                "totp": totp
            },
            timeout=10
        )

        d1 = r1.json().get("data", {})
        view_token = d1.get("token")
        view_sid = d1.get("sid")

        if not view_token or not view_sid:
            return False, "Login step-1 failed"

        # ---- STEP 2 ----
        r2 = requests.post(
            "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate",
            headers={
                **BASE_HEADERS,
                "Auth": view_token,
                "Sid": view_sid
            },
            json={"mpin": mpin},
            timeout=10
        )

        d2 = r2.json().get("data", {})
        auth_token = d2.get("token")
        auth_sid = d2.get("sid")
        base_url = d2.get("baseUrl")

        if not auth_token or not auth_sid:
            return False, "Login step-2 failed"

        # ---- SAVE AUTH (full session validity) ----
        auth_payload = {
            "AUTH_TOKEN": auth_token,
            "AUTH_SID": auth_sid,
            "BASE_URL": base_url,
            "LOGIN_TIME": int(time.time()),
            # assume market-day session (~8 hours)
            "EXPIRES_AT": int(time.time()) + 8 * 60 * 60
        }

        with open(AUTH_FILE, "w") as f:
            json.dump(auth_payload, f, indent=2)

        return True, "Kotak login successful ✅"

    except Exception as e:
        return False, str(e)

# =========================
# LOAD AUTH
# =========================
def load_auth():
    if not AUTH_FILE.exists():
        return None

    try:
        with open(AUTH_FILE) as f:
            data = json.load(f)

        if data.get("EXPIRES_AT", 0) < time.time():
            AUTH_FILE.unlink(missing_ok=True)
            return None

        return data

    except Exception:
        return None

# =========================
# GET AUTH HEADERS
# =========================
def get_auth_headers():
    auth = load_auth()
    if not auth:
        return None

    return {
        **BASE_HEADERS,
        "Auth": auth["AUTH_TOKEN"],
        "Sid": auth["AUTH_SID"]
    }

# =========================
# STREAMLIT LOGIN PAGE
# =========================
def login_page():
    st.subheader("🔐 Kotak Neo Login")

    mpin = st.text_input("Enter MPIN", type="password")

    if st.button("Login"):
        with st.spinner("Logging in..."):
            ok, msg = kotak_login(mpin)
            if ok:
                st.success(msg)
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error(msg)
