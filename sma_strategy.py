# strategy/sma_strategy.py
import pandas as pd
from datetime import datetime
import yfinance as yf
from tvDatafeed import TvDatafeed, Interval
import pytz

# ---------------------- CONFIG ----------------------
TV_USERNAME = "bedageravi605@gmail.com"
TV_PASSWORD = "Anujbedage@45678"
TOUCH_PCT = 0.25  # % distance to detect touch
IST = pytz.timezone("Asia/Kolkata")

# Map Streamlit intervals to TVDatafeed intervals
INTERVAL_MAP = {
    "1m": Interval.in_1_minute,
    "5m": Interval.in_5_minute,
    "15m": Interval.in_15_minute,
    "30m": Interval.in_30_minute,
    "60m": Interval.in_1_hour,
    "1d": Interval.in_daily,
    "1wk": Interval.in_weekly
}

# ---------------------- INIT TV ----------------------
try:
    tv = TvDatafeed(TV_USERNAME, TV_PASSWORD)
except:
    tv = TvDatafeed()  # anonymous login

# ---------------------- STRATEGY FUNCTION ----------------------
def run_stock_strategy(symbol, interval="5m", sma_periods=[200,377,610]):
    """
    Fetch data for a symbol and interval, calculate SMAs, distance %, and touch detection.
    Returns a list of dictionaries ready for Streamlit display.
    """
    tf_interval = INTERVAL_MAP.get(interval, Interval.in_5_minute)
    data_source = "TV"

    df = None

    # ---------------- TV DATA ----------------
    try:
        df = tv.get_hist(symbol=symbol, exchange="NSE", interval=tf_interval, n_bars=5000)
        if df is not None and not df.empty:
            # TVDatafeed returns UTC timestamps, convert to IST
            df.index = pd.to_datetime(df.index).tz_localize(pytz.UTC).tz_convert(IST)
    except:
        df = None

    # ---------------- YAHOO FINANCE FALLBACK ----------------
    if df is None or df.empty:
        try:
            if interval == "1wk":
                df = yf.download(f"{symbol}.NS", period="max", interval="1wk", progress=False)
            elif interval == "1d":
                df = yf.download(f"{symbol}.NS", period="2y", interval="1d", progress=False)
            else:
                df = yf.download(f"{symbol}.NS", period="60d", interval=interval, progress=False)

            if df.empty:
                return None

            # Make index tz-aware (assume UTC), then convert to IST
            df.index = pd.to_datetime(df.index)
            if df.index.tzinfo is None:
                df.index = df.index.tz_localize(pytz.UTC).tz_convert(IST)
            else:
                df.index = df.index.tz_convert(IST)

            # Ensure 'close' column exists
            if 'Close' in df.columns:
                df.rename(columns={"Close":"close"}, inplace=True)
            data_source = "Yahoo"

        except:
            return None

    # ---------------- CALCULATE SMAs ----------------
    for p in sma_periods:
        df[f"SMA{p}"] = df["close"].rolling(window=p).mean()

    # ---------------- LATEST DATA ----------------
    latest = df.iloc[-1]
    latest_close = round(latest["close"], 2)
    latest_time = latest.name

    # ---------------- FORMAT TIME IST ----------------
    if latest_time.tzinfo is None:
        latest_time = latest_time.tz_localize(pytz.UTC).tz_convert(IST)
    else:
        latest_time = latest_time.tz_convert(IST)
    latest_time_str = latest_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    # ---------------- SMA INFO ----------------
    smas_info = {}
    for p in sma_periods:
        val = latest.get(f"SMA{p}", None)
        if pd.isna(val):
            smas_info[p] = {"value": None, "distance": None, "touch": False}
        else:
            val = round(val, 2)
            dist = (latest_close - val)/val*100
            touch = abs(dist) <= TOUCH_PCT
            smas_info[p] = {
                "value": val,
                "distance": round(dist, 2),
                "touch": touch
            }

    return [{
        "symbol": symbol.upper(),
        "interval": interval,
        "data_source": data_source,
        "datetime": latest_time_str,
        "latest_close": latest_close,
        "smas": smas_info
    }]
