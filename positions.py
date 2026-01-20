import pandas as pd
import requests
from login import load_auth   # ✅ correct import

HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

def get_positions():
    """Fetch Kotak MTF positions from auth.json"""

    auth_data = load_auth()
    if not auth_data:
        return None, "Auth file not found. Please login first."

    base_url = auth_data.get("BASE_URL")
    if not base_url:
        return None, "BASE_URL missing. Please login again."

    HEADERS["Auth"] = auth_data.get("AUTH_TOKEN")
    HEADERS["Sid"] = auth_data.get("AUTH_SID")

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
