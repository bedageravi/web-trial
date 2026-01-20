import json
from pathlib import Path
import pandas as pd
import requests
from login import login  # import login module for auth file

HEADERS = {"Auth": None, "Sid": None, "neo-fin-key": "neotradeapi", "accept": "application/json"}

def get_positions():
    """Fetch Kotak MTF positions from auth.json"""
    auth_data = login.load_auth()
    if not auth_data:
        return None, "Auth file not found. Please login first."

    base_url = auth_data.get("BASE_URL")
    HEADERS["Auth"] = auth_data.get("AUTH_TOKEN")
    HEADERS["Sid"] = auth_data.get("AUTH_SID")

    try:
        r = requests.get(f"{base_url}/quick/user/positions", headers=HEADERS, timeout=10)
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching positions: {e}"

    # Filter only MTF positions
    mtf_positions = []
    for p in data:
        if p.get("prod") != "MTF":
            continue
        scrip = p.get("trdSym")
        qty = int(p.get("cfBuyQty",0)) + int(p.get("flBuyQty",0))
        avg_price = float(p.get("buyAmt",0)) + float(p.get("cfBuyAmt",0))
        mtf_positions.append({
            "Symbol": scrip,
            "Qty": qty,
            "AvgPrice": round(avg_price/qty,2) if qty>0 else 0
        })

    if not mtf_positions:
        return None, "No MTF positions found"

    df_positions = pd.DataFrame(mtf_positions)
    return df_positions, "Positions fetched successfully"
