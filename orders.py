import pandas as pd
import requests
import json
from login import get_auth_headers  # Use new auth.json headers
from datetime import datetime

def get_orders():
    """
    Fetch Kotak today’s orders using auth.json session.
    Returns a DataFrame of today's orders or None with message.
    """

    # Load headers from auth.json
    headers = get_auth_headers()
    if not headers:
        return None, "Auth token not found or expired. Please login first."

    # Get base_url from auth.json
    try:
        with open("auth.json", "r") as f:
            data = json.load(f)
        base_url = data.get("BASE_URL")
        if not base_url:
            return None, "BASE_URL missing. Please login again."
    except Exception as e:
        return None, f"Error reading auth.json: {e}"

    # Fetch orders from API
    try:
        r = requests.get(
            f"{base_url}/quick/user/orders",
            headers=headers,
            timeout=10
        )
        r.raise_for_status()
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching orders: {e}"

    # Filter orders from today
    today_str = datetime.now().strftime("%d-%b-%Y")
    today_orders = [
        o for o in data
        if o.get("ordDtTm", "").startswith(today_str)
    ]

    if not today_orders:
        return None, "No orders found today"

    # Prepare DataFrame
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
