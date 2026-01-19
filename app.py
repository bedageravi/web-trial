import streamlit as st
from datetime import datetime, timedelta, timezone
import random
import pyotp
import requests
from supabase import create_client
import pandas as pd

# ===============================
# SECRETS
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
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="ALGO TRADE ™", layout="wide")

# ===============================
# STYLE
# ===============================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg, #2b2b2b, #000000); }
[data-testid="stHeader"] { background: rgba(0,0,0,0.0); }
div.stButton > button { background-color: white; color: black; font-weight: bold; border-radius: 8px; height: 42px; width: 200px; }
</style>
""", unsafe_allow_html=True)

# ===============================
# HERO IMAGE
# ===============================
IMAGE_LIST = [
    "https://images.pexels.com/photos/6770775/pexels-photo-6770775.jpeg",
    "https://wallpapercave.com/wp/wp9587572.jpg",
    "https://images.pexels.com/photos/5834234/pexels-photo-5834234.jpeg"
]
selected_image = random.choice(IMAGE_LIST)
st.markdown(
    f"""<div style="display:flex; justify-content:center; padding-top:20px;">
        <img src="{selected_image}" style="width:420px; height:420px; border-radius:12px;" />
    </div>""",
    unsafe_allow_html=True
)

st.markdown("""
<div style="text-align:center; color:white; padding-top:10px; padding-bottom:25px;">
    <h1 style="font-size:42px;">Build Your Automated Trading System</h1>
    <h2 style="font-size:28px;">ALGO TRADE ™</h2>
</div>
""", unsafe_allow_html=True)

# ===============================
# HELPER FUNCTIONS
# ===============================

def load_auth():
    """Load latest auth session"""
    try:
        res = supabase.table("auth_sessions").select("*").order("created_at", desc=True).limit(1).execute()
        if res.data:
            rec = res.data[0]
            HEADERS["Auth"] = rec["auth_token"]
            HEADERS["Sid"] = rec["auth_sid"]
            return rec
    except Exception:
        return None
    return None

def get_latest_signal():
    """Fetch latest signal safely"""
    try:
        res = supabase.table("signals").select("*").order("created_at", desc=True).limit(1).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        st.warning(f"Supabase read warning (signals table missing?): {e}")
    return None

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

    # Step 1: tradeApiLogin
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

    # Step 2: tradeApiValidate
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

    # Save session
    try:
        supabase.table("auth_sessions").delete().neq("auth_token","").execute()
        record = {
            "auth_token": auth_token,
            "auth_sid": auth_sid,
            "base_url": base_url,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("auth_sessions").insert(record).execute()
    except Exception as e:
        return False, f"Supabase save failed: {e}"

    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid
    return True, "Kotak login successful ✅"

def auto_login():
    """Check latest signal; login only if old or missing"""
    latest_signal = get_latest_signal()
    now = datetime.now(timezone.utc)

    if latest_signal:
        created = datetime.fromisoformat(latest_signal["created_at"])
        if now - created <= timedelta(hours=4):
            st.success("✅ Latest signal is fresh, using existing session")
            return load_auth()

    # MPIN input with unique key
    st.info("Latest signal is old or missing. Please login with MPIN.")
    mpin = st.text_input("Enter MPIN", type="password", key="mpin_input")
    if st.button("Login", key="login_button"):
        success, msg = kotak_login(mpin)
        if success:
            st.success(msg)
            return load_auth()
        else:
            st.error(msg)
    return None

# ===============================
# DASHBOARD
# ===============================
auth_data = auto_login()

if auth_data:
    st.write("Session token:", auth_data["auth_token"])
    st.write("Base URL:", auth_data["base_url"])
    st.write("Session timestamp:", auth_data["created_at"])

    # ---------------------
    # Load positions
    # ---------------------
    try:
        from positions import get_positions
        df_pos, pos_msg = get_positions()
        if df_pos is not None and not df_pos.empty:
            st.subheader("📊 MTF Positions")
            st.dataframe(df_pos, use_container_width=True)
        else:
            st.warning(pos_msg)
    except Exception as e:
        st.error(f"Positions load error: {e}")

    # ---------------------
    # Load orders
    # ---------------------
    try:
        from orders import get_orders
        df_ord, ord_msg = get_orders()
        if df_ord is not None and not df_ord.empty:
            st.subheader("🧾 Today's Orders")
            st.dataframe(df_ord, use_container_width=True)
        else:
            st.warning(ord_msg)
    except Exception as e:
        st.error(f"Orders load error: {e}")
