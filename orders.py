import pandas as pd
import requests
from datetime import datetime
from login import get_auth_headers

def get_orders():
    headers = get_auth_headers()
    if not headers:
        return None, "Auth token not found. Please login first."

    base_url = headers.get("BASE_URL", headers.get("base_url", ""))
    if not base_url:
        return None, "BASE_URL missing. Please login again."

    try:
        r = requests.get(f"{base_url}/quick/user/orders", headers=headers, timeout=10)
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching orders: {e}"

    # Filter today's orders
    today_str = datetime.now().strftime("%d-%b-%Y")
    today_orders = [o for o in data if o.get("ordDtTm", "").startswith(today_str)]

    if not today_orders:
        return None, "No orders found today"

    orders_list = []
    for o in today_orders:
        orders_list.append({
            "Symbol": o.get("sym"),
            "Side": o.get("side"),
            "Qty": int(o.get("qty", 0)),
            "Price": round(float(o.get("avgPrc", 0)), 2),
            "OrderType": o.get("prod"),
            "Status": o.get("stat"),
            "Time": o.get("ordDtTm")
        })

    return pd.DataFrame(orders_list), "Orders fetched successfully"
