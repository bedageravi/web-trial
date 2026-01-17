import json
from pathlib import Path
import pandas as pd
import requests
from login import login  # import login module for auth file
from datetime import datetime

HEADERS = {"Auth": None, "Sid": None, "neo-fin-key": "neotradeapi", "accept": "application/json"}

def get_orders():
    """Fetch Kotak today’s orders from auth.json"""
    auth_data = login.load_auth()
    if not auth_data:
        return None, "Auth file not found. Please login first."

    base_url = auth_data.get("BASE_URL")
    HEADERS["Auth"] = auth_data.get("AUTH_TOKEN")
    HEADERS["Sid"] = auth_data.get("AUTH_SID")

    try:
        r = requests.get(f"{base_url}/quick/user/orders", headers=HEADERS, timeout=10)
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching orders: {e}"

    today_str = datetime.now().strftime("%d-%b-%Y")
    today_orders = [o for o in data if o.get("ordDtTm","").startswith(today_str)]

    if not today_orders:
        return None, "No orders found today"

    orders_list = []
    for o in today_orders:
        orders_list.append({
            "Symbol": o.get("sym"),
            "Side": o.get("side"),
            "Qty": int(o.get("qty",0)),
            "Price": round(float(o.get("avgPrc",0)),2),
            "OrderType": o.get("prod"),
            "Status": o.get("stat"),
            "Time": o.get("ordDtTm")
        })

    df_orders = pd.DataFrame(orders_list)
    return df_orders, "Orders fetched successfully"
