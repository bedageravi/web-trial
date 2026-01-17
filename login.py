import json
import pyotp
import requests
from datetime import datetime
from pathlib import Path

AUTH_FILE = Path("login/auth.json")  # save token here

# Kotak credentials (replace with your details)
ACCESS_TOKEN_SHORT = "ce5191a8-b2d3-44ff-bc3c-65970498e2f0"
MOBILE = "+919766728415"
UCC = "XXTBL"
MPIN = ""  # will take input
TOTP_SECRET = "OBEESAYVC2V3IA5YYHCN6EB7UI"

HEADERS = {"Auth": None, "Sid": None, "neo-fin-key": "neotradeapi", "accept": "application/json"}

def kotak_login(mpin_input: str):
    """Perform login and save auth.json"""
    global MPIN
    MPIN = mpin_input

    totp = pyotp.TOTP(TOTP_SECRET).now()
    headers = {
        "Authorization": ACCESS_TOKEN_SHORT,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    # Step 1: tradeApiLogin
    r1 = requests.post(
        "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin",
        headers=headers,
        json={"mobileNumber": MOBILE, "ucc": UCC, "totp": totp}
    )
    data1 = r1.json().get("data", {})
    view_token = data1.get("token")
    view_sid = data1.get("sid")

    if not view_token or not view_sid:
        return False, "Step1 login failed"

    # Step 2: tradeApiValidate
    headers2 = headers.copy()
    headers2["sid"] = view_sid
    headers2["Auth"] = view_token

    r2 = requests.post(
        "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate",
        headers=headers2,
        json={"mpin": MPIN}
    )
    data2 = r2.json().get("data", {})

    auth_token = data2.get("token")
    auth_sid = data2.get("sid")
    base_url = data2.get("baseUrl")

    if not auth_token or not auth_sid:
        return False, "Step2 validate failed"

    # Save auth.json
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump({"AUTH_TOKEN": auth_token, "AUTH_SID": auth_sid, "BASE_URL": base_url}, f, indent=2)

    HEADERS["Auth"] = auth_token
    HEADERS["Sid"] = auth_sid

    return True, "Login successful"

def load_auth():
    """Load existing auth.json"""
    if AUTH_FILE.exists():
        with open(AUTH_FILE, "r") as f:
            return json.load(f)
    return None
