import streamlit as st
from datetime import datetime, timedelta, timezone
from supabase import create_client
import pyotp
import requests

# ===============================
# STREAMLIT SECRETS
# ===============================
ACCESS_TOKEN_SHORT = st.secrets["kotak"]["ACCESS_TOKEN_SHORT"]
MOBILE = st.secrets["kotak"]["mobile"]
UCC = st.secrets["kotak"]["ucc"]
TOTP_SECRET = st.secrets["kotak"]["totp_secret"]

SUPABASE_URL = st.secrets["kotak"]["url"]
SUPABASE_SERVICE_KEY = st.secrets["kotak"]["service_key"]

# ===============================
# SUPABASE CLIENT
# ===============================
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ===============================
# HEADERS FOR KOTAK API
# ===============================
HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

# ===============================
# LOAD LATEST SUPA SIGNAL
# ===============================
def get_latest_signal():
    """Return latest signal row from Supabase"""
    try:
        res = (
            supabase
            .table("signals")  # replace with your signal table
            .select("*")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if res.data:
            return res.data[0]
    except Exception as e:
        st.warning(f"Supabase read error: {e}")
    return None

# ===============================
# KOTAK LOGIN
# ===============================
def kotak_login(mpin_input: str):
    """Perform Kotak Neo login and save session"""
    try:
        totp = pyotp.TOTP(TOTP_SECRET.strip().replace(" ", "")).now()
    except Exception as e:
        return False, f"TOTP error: {e}"

    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    # Step1
    try:
        r1 = requests.post(
            "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin",
            headers=headers,
            json={"mobileNumber": MOBILE, "ucc": UCC, "totp": totp},
            timeout=10
        )
        d1 = r1.json().get("data", {})
        view_token = d1.get("token")
        view_sid = d1.get("sid")
    except Exception as e:
        return False, f"Step1 failed: {e}"

    if not view_token or not view_sid:
        return False, "Invalid Step1 response"

    # Step2
    headers2 = headers.copy()
    headers2["Auth"] = view_token
    headers2["sid"] = view_sid

    try:
        r2 = requests.post(
            "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate",
            headers=headers2,
            json={"mpin": mpin_input},
            timeout=10
        )
        d2 = r2.json().get("data", {})
        auth_token = d2.get("token")
        auth_sid = d2.get("sid")
        base_url = d2.get("baseUrl")
    except Exception as e:
        return False, f"Step2 failed: {e}"

    if not auth_token or not auth_sid or not base_url:
        return False, "Invalid Step2 response"

    # Save session (replace old)
    try:
        supabase.table("auth_sessions").delete().neq("auth_token", "").execute()
        record = {
            "auth_token": auth_token,
            "auth_sid": auth_sid,
            "base_url": base_url,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("auth_sessions").insert(record).execute()
    except Exception as e:
        return False, f"Supabase save failed: {e}"

    # Set headers
    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "Kotak login successful ✅"

# ===============================
# LOAD AUTH (LATEST SESSION)
# ===============================
def load_auth():
    """Load latest session"""
    try:
        res = (
            supabase
            .table("auth_sessions")
            .select("*")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if res.data:
            rec = res.data[0]
            HEADERS["Auth"] = rec["auth_token"]
            HEADERS["Sid"] = rec["auth_sid"]
            return rec
    except Exception:
        return None
    return None

# ===============================
# AUTO-LOGIN LOGIC
# ===============================
def auto_login():
    """Check latest signal; if recent, skip MPIN login"""
    latest_signal = get_latest_signal()
    now = datetime.now(timezone.utc)

    # If latest signal exists and is within last 4 hours, skip login
    if latest_signal:
        created = datetime.fromisoformat(latest_signal["created_at"])
        if now - created <= timedelta(hours=4):
            st.success("✅ Latest signal is fresh, using existing session")
            return load_auth()

    # Otherwise, ask for MPIN
    st.info("Latest signal is old or missing. Please login with MPIN.")
    mpin = st.text_input("Enter MPIN", type="password")
    if st.button("Login"):
        success, msg = kotak_login(mpin)
        if success:
            st.success(msg)
            return load_auth()
        else:
            st.error(msg)
    return None

# ===============================
# RUN AUTO LOGIN
# ===============================
auth_data = auto_login()
if auth_data:
    st.write("Current session token:", auth_data["auth_token"])
    st.write("Base URL:", auth_data["base_url"])
    st.write("Session timestamp:", auth_data["created_at"])
