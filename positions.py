import pandas as pd
import requests
from login import get_auth_headers  # Use new auth.json headers

def get_positions():
    """
    Fetch Kotak MTF positions using auth.json session.
    Returns a DataFrame of MTF positions or None with message.
    """

    # Load headers from auth.json
    headers = get_auth_headers()
    if not headers:
        return None, "Auth token not found or expired. Please login first."

    # Get base_url from auth.json
    auth_data = headers  # headers still contains only Auth/Sid
    try:
        with open("auth.json", "r") as f:
            data = json.load(f)
        base_url = data.get("BASE_URL")
        if not base_url:
            return None, "BASE_URL missing. Please login again."
    except Exception as e:
        return None, f"Error reading auth.json: {e}"

    try:
        r = requests.get(
            f"{base_url}/quick/user/positions",
            headers=headers,
            timeout=10
        )
        r.raise_for_status()
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching positions: {e}"

    # Filter only MTF positions
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

    # Create summary
    total_pnl = sum([p.get("Qty", 0) * p.get("AvgPrice", 0) for p in mtf_positions])
    total_pct = 0  # You can calculate % return if needed

    summary = {
        "total_pnl": round(total_pnl, 2),
        "total_pct": total_pct
    }

    return pd.DataFrame(mtf_positions), summary
