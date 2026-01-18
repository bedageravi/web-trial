# -------------------- positions.py --------------------
import pandas as pd
import requests
from login import load_auth, supabase
from datetime import datetime, timezone

HEADERS = {
    "Auth": None,
    "Sid": None,
    "neo-fin-key": "neotradeapi",
    "accept": "application/json"
}

# -------------------- Fetch Positions --------------------
def get_positions():
    """
    Fetch Kotak MTF positions and return DataFrame + summary
    Columns: Symbol, Qty, AvgPrice, LTP, P&L (₹), % Return, Status, ExitPrice
    summary: dict(total_pnl, total_pct)
    """
    auth_data = load_auth()
    if not auth_data:
        return None, ("Auth token not found. Please login first",)

    base_url = auth_data.get("base_url")
    if not base_url:
        return None, ("BASE_URL missing. Please login again",)

    HEADERS["Auth"] = auth_data.get("auth_token")
    HEADERS["Sid"] = auth_data.get("auth_sid")

    try:
        r = requests.get(f"{base_url}/quick/user/positions", headers=HEADERS, timeout=10)
        data = r.json().get("data", [])
    except Exception as e:
        return None, (f"Error fetching positions: {e}",)

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
        return None, ("No MTF positions found",)

    df_positions = pd.DataFrame(mtf_positions)

    # -------------------- Simulate LTP (replace with live LTP later) --------------------
    ltp_data = {row["Symbol"]: row["AvgPrice"]*1.02 for _, row in df_positions.iterrows()}  # example +2%

    df_positions["LTP"] = df_positions["Symbol"].map(lambda x: ltp_data.get(x, 0))
    df_positions["P&L (₹)"] = round((df_positions["LTP"] - df_positions["AvgPrice"]) * df_positions["Qty"], 2)
    df_positions["% Return"] = round(((df_positions["LTP"] - df_positions["AvgPrice"]) / df_positions["AvgPrice"])*100, 2)
    df_positions["Status"] = "RUN"
    df_positions["ExitPrice"] = None

    # -------------------- Detect Exit --------------------
    exit_records = []
    if "last_snapshot" not in globals():
        globals()["last_snapshot"] = {row["Symbol"]: row["Qty"] for _, row in df_positions.iterrows()}

    for idx, row in df_positions.iterrows():
        sym = row["Symbol"]
        qty = row["Qty"]
        avg_price = row["AvgPrice"]
        ltp = row["LTP"]
        last_qty = globals()["last_snapshot"].get(sym, 0)

        if last_qty > qty:
            exit_qty = last_qty - qty
            exit_price = ltp
            df_positions.at[idx, "ExitPrice"] = exit_price
            df_positions.at[idx, "Status"] = "EXIT" if qty == 0 else "PARTIAL_EXIT"

            pnl = (exit_price - avg_price) * exit_qty
            pct = ((exit_price - avg_price)/avg_price)*100
            exit_records.append({
                "Symbol": sym,
                "Qty": exit_qty,
                "AvgPrice": avg_price,
                "ExitPrice": exit_price,
                "P&L": round(pnl, 2),
                "PercentReturn": round(pct, 2),
                "trade_date": datetime.now().isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

    # Update snapshot
    globals()["last_snapshot"] = {row["Symbol"]: row["Qty"] for _, row in df_positions.iterrows()}

    # -------------------- Save Exits --------------------
    if exit_records:
        supabase.table("positions_history").insert(exit_records).execute()

    # -------------------- Summary --------------------
    total_pnl = df_positions["P&L (₹)"].sum()
    total_pct = df_positions["% Return"].mean()

    summary = {"total_pnl": round(total_pnl,2), "total_pct": round(total_pct,2)}

    return df_positions, summary
