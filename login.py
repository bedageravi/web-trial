import streamlit as st
import pyotp
import requests
from datetime import datetime, timezone
from supabase import create_client

# ==================================================
# STREAMLIT SECRETS
# ==================================================
ACCESS_TOKEN_SHORT = st.secrets["kotak"]["ACCESS_TOKEN_SHORT"]
MOBILE = st.secrets["kotak"]["mobile"]
UCC = st.secrets["kotak"]["ucc"]
TOTP_SECRET = st.secrets["kotak"]["totp_secret"]

SUPABASE_URL = st.secrets["kotak"]["url"]

# ⚠️ USE SERVICE ROLE KEY (IMPORTANT)
SUPABASE_SERVICE_KEY = st.secrets["kotak"]["anon_key"]

# ==================================================
# SUPABASE CLIENT
# ==================================================
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ==================================================
# GLOBAL HEADERS (RUNTIME)
# ==================================================
HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

# ==================================================
# KOTAK LOGIN
# ==================================================
def kotak_login(mpin_input: str):
    """Perform Kotak Neo login and store ONLY latest session in Supabase"""

    if not mpin_input:
        return False, "MPIN cannot be empty"

    try:
        totp = pyotp.TOTP(TOTP_SECRET.strip().replace(" ", "")).now()
    except Exception as e:
        return False, f"TOTP error: {e}"

    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    # ---------- STEP 1 ----------
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
        return False, f"Login step1 failed: {e}"

    if not view_token or not view_sid:
        return False, "Invalid response in login step1"

    # ---------- STEP 2 ----------
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
        return False, f"Login step2 failed: {e}"

    if not auth_token or not auth_sid or not base_url:
        return False, "Invalid response in login step2"

    # ==================================================
    # SAVE SESSION (DELETE OLD → INSERT NEW)
    # ==================================================
    try:
        # clear old sessions
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

    # set runtime headers
    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "Kotak login successful ✅"

# ==================================================
# LOAD AUTH (ALWAYS LATEST)
# ==================================================
def load_auth():
    """Load latest valid auth session from Supabase"""

    try:
        res = (
            supabase
            .table("auth_sessions")
            .select("*")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception:
        return None

    if not res.data:
        return None

    rec = res.data[0]
    HEADERS["Auth"] = rec["auth_token"]
    HEADERS["Sid"] = rec["auth_sid"]
    return rec

# ==================================================
# LOGOUT (REAL LOGOUT)
# ==================================================
def logout():
    """Clear Supabase session and Streamlit state"""
    try:
        supabase.table("auth_sessions").delete().neq("auth_token", "").execute()
    except Exception:
        pass

    HEADERS["Auth"] = None
    HEADERS["Sid"] = None
    st.session_state.logged_in = False

# ==================================================
# STREAMLIT LOGIN UI
# ==================================================
def login_page():
    st.subheader("🔐 Kotak Neo Login")

    mpin = st.text_input("Enter MPIN", type="password")

    if st.button("Login"):
        with st.spinner("Logging in..."):
            success, msg = kotak_login(mpin)
            if success:
                st.session_state.logged_in = True
                st.success(msg)
            else:
                st.error(msg)
