import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# =============================
# AUTO-REFRESH
# =============================
st_autorefresh(interval=60*1000, limit=None, key="auto_refresh")

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="ALGO TRADE ™", layout="wide")

# =============================
# COLOR FLOW / GRADIENT BACKGROUND
# =============================
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #6a0dad, #8A2BE2, #4B0082);
        background-size: 400% 400%;
        animation: gradientFlow 15s ease infinite;
    }

    @keyframes gradientFlow {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    [data-testid="stToolbar"] {right: 1rem;}
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# TRADEMARK HEADER
# =============================
st.markdown(
    """
    <div style="display:flex; align-items:center; gap:15px; padding:10px 20px;">
        <img src="https://cdn.pixabay.com/photo/2020/06/11/19/40/bull-5284793_1280.jpg" width="50" height="50" style="border-radius:50%;">
        <h2 style="color:white; margin:0; font-family:'Arial',sans-serif;">ALGO TRADE ™</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================
# HERO SECTION
# =============================
st.markdown(
    """
    <div style="text-align:center; padding-top:20px; padding-bottom:40px; 
                color:white; text-shadow:2px 2px 8px rgba(0,0,0,0.7);">
        <h1 style="font-size:60px; margin-bottom:0;">Build Your System with</h1>
        <h2 style="font-size:40px;">ALGO TRADE ™</h2>
    </div>
    """,
    unsafe_allow_html=True
)


# =============================
# GLASSMORPHIC TABLE FUNCTION
# =============================
def glass_card(title, df):
    st.markdown(
        f"""
        <div style="
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: white;
        ">
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.dataframe(df, use_container_width=True)

# =============================
# DISPLAY TABLES
# =============================
col1, col2 = st.columns(2)
with col1:
    glass_card("📊 MTF Positions", df_positions)
with col2:
    glass_card("🧾 Today's Orders", df_orders)
