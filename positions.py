# -------------------- positions.py --------------------
import pandas as pd
import requests
from login import load_auth, supabase  # Supabase client & login
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
    Fetch Kotak MTF positions and return DataFrame.
    Columns: Symbol, Qty, AvgPrice, LTP, P&L (₹), % Return, Status, ExitPrice
    """
    auth_data = load_auth()
    if not auth_data:
        return None, "Auth token not found. Please login first."

    base_url = auth_data.get("base_url")
    if not base_url:
        return None, "BASE_URL missing. Please login again."

    HEADERS["Auth"] = auth_data.get("auth_token")
    HEADERS["Sid"] = auth_data.get("auth_sid")

    try:
        r = requests.get(f"{base_url}/quick/user/positions", headers=HEADERS, timeout=10)
        data = r.json().get("data", [])
    except Exception as e:
        return None, f"Error fetching positions: {e}"

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

    df_positions = pd.DataFrame(mtf_positions)
    return df_positions, "Positions fetched successfully"


# -------------------- Update LTP and P&L --------------------
def update_positions_ltp(df_positions, ltp_data, last_snapshot={}):
    """
    ltp_data: dict {symbol: latest_price}
    last_snapshot: dict {symbol: last_qty} to detect exits
    """
    df_positions["LTP"] = df_positions["Symbol"].map(lambda x: ltp_data.get(x, 0))
    df_positions["P&L (₹)"] = 0.0
    df_positions["% Return"] = 0.0
    df_positions["Status"] = "RUN"
    df_positions["ExitPrice"] = None

    exit_records = []

    for idx, row in df_positions.iterrows():
        sym = row["Symbol"]
        qty = row["Qty"]
        avg_price = row["AvgPrice"]
        ltp = row["LTP"]

        last_qty = last_snapshot.get(sym, 0)

        # Detect partial/full exit
        if last_qty > qty:
            exit_qty = last_qty - qty
            exit_price = ltp  # assume exit at last LTP

            # Determine status
            df_positions.at[idx, "ExitPrice"] = exit_price
            if qty == 0:
                df_positions.at[idx, "Status"] = "EXIT"
            else:
                df_positions.at[idx, "Status"] = "PARTIAL_EXIT"

            pnl = (exit_price - avg_price) * exit_qty
            pct_return = ((exit_price - avg_price)/avg_price)*100

            exit_records.append({
                "Symbol": sym,
                "Qty": exit_qty,
                "AvgPrice": avg_price,
                "ExitPrice": exit_price,
                "P&L": round(pnl, 2),
                "PercentReturn": round(pct_return, 2),
                "trade_date": datetime.now().isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        # For running positions
        df_positions.at[idx, "P&L (₹)"] = round((ltp - avg_price) * qty, 2) if qty > 0 else 0
        df_positions.at[idx, "% Return"] = round(((ltp - avg_price)/avg_price)*100, 2) if qty > 0 else 0

    return df_positions, exit_records


# -------------------- Save Exited Trades to Supabase --------------------
def save_exited_positions(exit_records):
    """
    Save only EXIT / PARTIAL_EXIT trades to Supabase
    """
    if not exit_records:
        return "No exited trades to save"

    supabase.table("positions_history").insert(exit_records).execute()
    return f"{len(exit_records)} exited trades saved to Supabase ✅"


# -------------------- Example Usage --------------------
if __name__ == "__main__":
    # Step 1: fetch positions
    df_pos, msg = get_positions()
    if df_pos is not None:
        # Step 2: simulate LTP (replace with real LTP fetch)
        ltp_data = {row["Symbol"]: row["AvgPrice"]*1.02 for _, row in df_pos.iterrows()}  # +2% example
        last_snapshot = {row["Symbol"]: row["Qty"] for _, row in df_pos.iterrows()}

        # Step 3: update positions with LTP & detect exit
        df_pos, exit_records = update_positions_ltp(df_pos, ltp_data, last_snapshot)

        # Step 4: save exited positions
        msg_save = save_exited_positions(exit_records)

        # Step 5: display
        print(df_pos)
        print(msg_save)
