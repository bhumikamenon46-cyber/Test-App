# app.py
# fx-991EX-inspired Scientific Calculator (Streamlit)
# Black/ClassWiz style. Input and result shown same size & responsive.
# Keyboard input supported (type in the input box or use the hidden keyboard listener).
# SHIFT is functional: press SHIFT then a trig key to insert inverse trig.

import streamlit as st
import math
import re
from math import factorial

# ---------------- Page config ----------------
st.set_page_config(page_title="fx-991 Inspired Calculator", page_icon="🧮", layout="wide")

# ---------------- Styling ----------------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700&family=Inter:wght@300;400;600&display=swap');

:root{
  --bg: #070708;
  --panel: #0f1113;
  --display:#050607;
  --muted: #9aa4b2;
  --accent: #2f9cff;
  --key-dark: #141516;
  --key-top: #1e1f22;
  --glass: rgba(255,255,255,0.03);
}

body { background: var(--bg); color: #eaf0f7; }

/* Container card */
.calc-card {
  max-width: 1100px;
  margin: 18px auto;
  background: linear-gradient(180deg,#111214,#0b0c0d);
  border-radius: 14px;
  padding: 18px;
  border: 1px solid var(--glass);
  box-shadow: 0 10px 40px rgba(0,0,0,0.6);
}

/* Display row: two equal blocks responsive */
.display-row {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.display-block {
  flex: 1 1 48%;
  background: linear-gradient(180deg,#020204,#0b0f13);
  border-radius:10px;
  padding: 14px 16px;
  min-height:72px;
  font-family: 'Orbitron', monospace;
  font-size:28px;
  color: #ffffff;
  text-align: right;
  border: 1px solid rgba(255,255,255,0.04);
  box-shadow: inset 0 -6px 18px rgba(0,0,0,0.6);
  display:flex;
  align-items:center;
  justify-content:flex-end;
  word-break:break-all;
}

/* label under display */
.display-sub {
  color: var(--muted);
  font-size:13px;
  margin-bottom: 12px;
  text-align: right;
}

/* keys layout */
.keys { display:grid; gap:10px; }
.grid-6 { grid-template-columns: repeat(6, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

/* button look - we use Streamlit buttons for functionality but style containers to look like keys */
.key {
  background: linear-gradient(180deg,#1b1c1e,#0f1011);
  border-radius:10px;
  padding: 10px 6px;
  text-align:center;
  font-weight:700;
  border:1px solid rgba(255,255,255,0.02);
  user-select:none;
}
.key-small { font-size:14px; color:var(--muted); }
.key-ac { background: linear-gradient(180deg,#6a1f1f,#3a0f0f); color:white; }
.key-eq { background: linear-gradient(180deg,#0f7a48,#055a33); color:white; font-weight:800; }
.key-alt { background: linear-gradient(180deg,#26272a,#141416); color:var(--muted); }

.side-panel {
  background: linear-gradient(180deg,#0f1113,#090a0b);
  border-radius:12px;
  padding:12px;
  border:1px solid var(--glass);
}

/* Hide the actual Streamlit button border so styled container looks like key */
.stButton>button {
  background: transparent !important;
  border: none !important;
  width: 100%;
  height: 100%;
  color: inherit;
  font-weight: 700;
}
[data-testid="stVerticalBlock"] > div { gap:8px; }

/* Make display text selectable for copy */
.display-block .stCopyBtn { display:none; }
</style>
""", unsafe_allow_html=True)

# ---------------- Safe math environment and wrappers ----------------

# Trig wrappers: when in DEG mode convert degrees -> radians for sin/cos/tan,
# and inverse trig returns degrees if DEG mode.
def sin_wr(x):
    x = float(x)
    return math.sin(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.sin(x)

def cos_wr(x):
    x = float(x)
    return math.cos(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.cos(x)

def tan_wr(x):
    x = float(x)
    return math.tan(math.radians(x)) if st.session_state.angle_mode == "DEG" else math.tan(x)

def asin_wr(x):
    res = math.asin(float(x))
    return math.degrees(res) if st.session_state.angle_mode == "DEG" else res

def acos_wr(x):
    res = math.acos(float(x))
    return math.degrees(res) if st.session_state.angle_mode == "DEG" else res

def atan_wr(x):
    res = math.atan(float(x))
    return math.degrees(res) if st.session_state.angle_mode == "DEG" else res

SAFE = {
    "pi": math.pi,
    "e": math.e,
    "sin": sin_wr,
    "cos": cos_wr,
    "tan": tan_wr,
    "asin": asin_wr,
    "acos": acos_wr,
    "atan": atan_wr,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "log": math.log,      # natural log
    "ln": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "abs": abs,
    "pow": pow,
    "factorial": factorial,
    "exp": math.exp,
    "rad": math.radians,
    "deg": math.degrees,
}

# ---------------- Session state ----------------
if "expr" not in st.session_state:
    st.session_state.expr = ""
if "last" not in st.session_state:
    st.session_state.last = ""
if "memory" not in st.session_state:
    st.session_state.memory = 0.0
if "angle_mode" not in st.session_state:
    st.session_state.angle_mode = "DEG"  # DEG or RAD
if "shift" not in st.session_state:
    st.session_state.shift = False  # SHIFT functional toggle
if "keyboard_input" not in st.session_state:
    st.session_state.keyboard_input = ""
if "eval_on_enter" not in st.session_state:
    st.session_state.eval_on_enter = True

# -----
