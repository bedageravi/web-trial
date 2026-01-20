import json
import pyotp
import requests
import streamlit as st
from pathlib import Path

# =========================
# SAFE AUTH FILE
# =========================
AUTH_FILE = Path("auth.json")

# =========================
# LOAD SECRETS
# =========================
ACCESS_TOKEN_SHORT = st.secrets["KOTAK_ACCESS_TOKEN"]
MOBILE = st.secrets["KOTAK_MOBILE"]
UCC = st.secrets["KOTAK_UCC"]
TOTP_SECRET = st.secrets["KOTAK_TOTP_SECRET"]

HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

# =========================
# KOTAK LOGIN LOGIC (UNCHANGED)
# =========================
def kotak_login(mpin_input: str):
    totp = pyotp.TOTP(TOTP_SECRET).now()

    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    # STEP 1
    r1 = requests.post(
        "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin",
        headers=headers,
        json={"mobileNumber": MOBILE, "ucc": UCC, "totp": totp}
    )

    data1 = r1.json().get("data", {})
    view_token = data1.get("token")
    view_sid = data1.get("sid")

    if not view_token or not view_sid:
        return False, "Step 1 login failed"

    # STEP 2
    headers2 = headers.copy()
    headers2["sid"] = view_sid
    headers2["Auth"] = view_token

    r2 = requests.post(
        "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate",
        headers=headers2,
        json={"mpin": mpin_input}
    )

    data2 = r2.json().get("data", {})
    auth_token = data2.get("token")
    auth_sid = data2.get("sid")
    base_url = data2.get("baseUrl")

    if not auth_token or not auth_sid:
        return False, "Step 2 validation failed"

    # SAVE AUTH (TEMP SAFE)
    with open(AUTH_FILE, "w") as f:
        json.dump(
            {"AUTH_TOKEN": auth_token, "AUTH_SID": auth_sid, "BASE_URL": base_url},
            f,
            indent=2
        )

    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "Kotak login successful"

# =========================
# STREAMLIT UI WRAPPER
# =========================
def login_page():
    st.subheader("🔐 Kotak Neo Login")

    mpin = st.text_input("Enter MPIN", type="password")

    if st.button("Login to Kotak"):
        success, msg = kotak_login(mpin)

        if success:
            st.session_state.logged_in = True
            st.success(msg)
        else:
            st.error(msg)
