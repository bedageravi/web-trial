import json
import pyotp
import requests
import streamlit as st
from pathlib import Path

AUTH_FILE = Path("auth.json")

ACCESS_TOKEN_SHORT = st.secrets["kotak"]["access_token"]
MOBILE = st.secrets["kotak"]["mobile"]
UCC = st.secrets["kotak"]["ucc"]
TOTP_SECRET = st.secrets["kotak"]["totp_secret"]

HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

def kotak_login(mpin_input: str):
    totp = pyotp.TOTP(TOTP_SECRET).now()
    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

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

    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump({"AUTH_TOKEN": auth_token, "AUTH_SID": auth_sid, "BASE_URL": base_url}, f, indent=2)

    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "Kotak login successful ✅"

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

def load_auth():
    if AUTH_FILE.exists():
        with open(AUTH_FILE, "r") as f:
            return json.load(f)
    return None
