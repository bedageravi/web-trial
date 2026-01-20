import pandas as pd
import requests
from login import get_auth_headers

def get_positions():
    headers = get_auth_headers()
    if not headers:
        return None, "Auth token not found. Please login first."

    base_url = headers.get("BASE_URL", headers.get("base_url", ""))
    if not base_url:
        return None, "BASE_URL missing. Please login again."

    try:
        r = requests.get(f"{base_url}/quick/user/positions", headers=headers, timeout=10)
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching positions: {e}"

    # Filter MTF positions
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

    # Summary
    total_pnl = sum([float(p.get("Qty",0)) * float(p.get("AvgPrice",0)) for p in mtf_positions])
    total_pct = round(total_pnl / 1000, 2)  # example placeholder

    summary = {"total_pnl": total_pnl, "total_pct": total_pct}
    return pd.DataFrame(mtf_positions), summary
