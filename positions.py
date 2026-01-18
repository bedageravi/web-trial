import pandas as pd
import requests
from login import load_auth
from tvDatafeed import TvDatafeed, Interval
import streamlit as st

# ---------------- TV LOGIN ----------------
TV_USERNAME = "bedageravi605@gmail.com"
TV_PASSWORD = "Anujbedage@45678"

_tv = None

def get_tv():
    """Login to TV only once"""
    global _tv
    if _tv is None:
        try:
            _tv = TvDatafeed(TV_USERNAME, TV_PASSWORD)
        except Exception as e:
            print("TV login failed:", e)
            _tv = None
    return _tv

# ---------------- CACHE LTP ----------------
@st.cache_data(ttl=60)
def get_ltp(symbol, exchange="NSE"):
    """Fetch latest LTP from TradingView, cached 60 sec"""
    tv = get_tv()
    if tv is None:
        return None
    try:
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_1_minute,
            n_bars=1
        )
        if df is None or df.empty:
            return None
        return float(df["close"].iloc[-1])
    except Exception as e:
        print(f"LTP fetch failed for {symbol}: {e}")
        return None

# ---------------- KOTAK HEADERS ----------------
HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

# ---------------- SAFE CAST ----------------
def safe_int(v):
    try:
        return int(v)
    except:
        return 0

def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

# ---------------- MAIN FUNCTION ----------------
def get_positions():
    auth_data = load_auth()
    if not auth_data:
        return None, "Auth token not found. Please login first."

    base_url = auth_data.get("base_url")
    if not base_url:
        return None, "BASE_URL missing. Please login again."

    HEADERS["Auth"] = auth_data.get("auth_token")
    HEADERS["Sid"] = auth_data.get("auth_sid")

    try:
        r = requests.get(
            f"{base_url}/quick/user/positions",
            headers=HEADERS,
            timeout=10
        )
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching positions: {e}"

    rows = []
    total_pnl = 0.0
    total_invested = 0.0

    for p in data:
        if p.get("prod") != "MTF":
            continue

        symbol = p.get("trdSym")
        qty = safe_int(p.get("cfBuyQty")) + safe_int(p.get("flBuyQty"))
        if qty <= 0:
            continue

        buy_amt = safe_float(p.get("buyAmt")) + safe_float(p.get("cfBuyAmt"))
        avg_price = round(buy_amt / qty, 2) if buy_amt > 0 else 0

        # ---------------- LTP & P&L ----------------
        ltp = get_ltp(symbol)
        if ltp is None:
            ltp = 0
            pnl = 0
            pct = 0
        else:
            pnl = round((ltp - avg_price) * qty, 2)
            pct = round(((ltp - avg_price) / avg_price) * 100, 2) if avg_price > 0 else 0

        total_pnl += pnl
        total_invested += buy_amt

        rows.append({
            "Symbol": symbol,
            "Qty": qty,
            "AvgPrice": avg_price,
            "LTP": round(ltp, 2),
            "P&L (₹)": pnl,
            "% Return": pct
        })

    if not rows:
        return None, "No MTF positions found"

    df = pd.DataFrame(rows)

    summary = {
        "total_pnl": round(total_pnl, 2),
        "total_pct": round((total_pnl / total_invested) * 100, 2) if total_invested > 0 else 0
    }

    return df, summary
