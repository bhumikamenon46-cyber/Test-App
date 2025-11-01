# app.py
# fx-991EX ClassWiz-inspired Scientific Calculator (Streamlit)
# White text on black display (ClassWiz style)

import streamlit as st
import math
import re
from math import factorial

st.set_page_config(page_title="fx-991EX Inspired Calculator", page_icon="🧮", layout="wide")

# --- CSS (ClassWiz-like premium black + white-display) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700&family=Inter:wght@300;400;600&display=swap');
    :root{--bg:#0b0c0d; --panel:#0f1113; --key:#151617; --muted:#98a0aa; --accent:#2f9cff; --accent-2:#ff9f1c; --glass: rgba(255,255,255,0.03);} 
    body { background: var(--bg); color: #eaf0f7; }
    .card { background: linear-gradient(180deg,#111214,#0b0c0d); border-radius:14px; padding:18px; border:1px solid var(--glass); box-shadow: 0 8px 30px rgba(0,0,0,0.7); }
    .display { background: linear-gradient(180deg,#020204,#0b0f13); border-radius:8px; padding:14px 18px; font-family: 'Orbitron', monospace; font-size:36px; color:#ffffff; text-align:right; min-height:64px; letter-spacing:1px; border:1px solid rgba(255,255,255,0.04); }
    .sub { color:var(--muted); font-size:13px; text-align:right; margin-top:6px; }
    .keys { display:grid; gap:10px; }
    .grid-6 { grid-template-columns: repeat(6, 1fr); }
    .grid-4 { grid-template-columns: repeat(4, 1fr); }
    .btn { background: linear-g
