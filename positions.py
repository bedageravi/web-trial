import pandas as pd
import requests
from login import load_auth   # ✅ use new Supabase-based login

HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

def get_positions(user_id="default_user"):
    """Fetch Kotak MTF positions using Supabase auth"""

    auth_data = load_auth(user_id)
    if not auth_data:
        return None, "Auth token not found. Please login first."

    base_url = auth_data.get("base_url")
    if not base_url:
        return None, "BASE_URL missing. Please login again."

    HEADERS["Auth"] = auth_data.get("auth_token")
    HEADERS["Sid"] = auth_data.get("sid")

    try:
        r = requests.get(
            f"{base_url}/quick/user/positions",
            headers=HEADERS,
            timeout=10
        )
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching positions: {e}"

    # === SAME MTF LOGIC AS YOUR PC SCRIPT ===
    mtf_positions = []

    for p in data:
        if p.get("prod") != "MTF":
            continue

        qty = int(p.get("cfBuyQty", 0)) + int(p.get("flBuyQty", 0))
        buy_amt = float(p.get("buyAmt", 0)) + float(p.get("cfBuyAmt", 0))

        mtf_positions.append({
            "Symbol": p.get("trdSym"),
            "Qty": qty,
            "AvgPrice": round(buy_amt / qty, 2) if qty > 0 else 0
        })

    if not mtf_positions:
        return None, "No MTF positions found"

    return pd.DataFrame(mtf_positions), "Positions fetched successfully"
