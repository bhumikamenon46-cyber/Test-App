# app.py
# Casio fx-991 inspired Scientific Calculator (Streamlit)
# Black/ClassWiz style. Input and result shown in equal-sized display blocks.
# Safe eval + DEG/RAD handling + SHIFT toggle (functional) + memory + Ans

import streamlit as st
import math
import re
from math import factorial

# ---------------- Page config ----------------
st.set_page_config(page_title="fx-991 Inspired Scientific Calculator", page_icon="🧮", layout="wide")

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
  --green: #0f7a48;
}

body { background: var(--bg); color: #eaf0f7; }

/* Card */
.calc-card {
  background: linear-gradient(180deg,#111214,#0b0c0d);
  border-radius: 14px;
  padding: 18px;
  border: 1px solid var(--glass);
  box-shadow: 0 10px 40px rgba(0,0,0,0.6);
}

/* Display row: two equal blocks */
.display-row {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
}
.display-block {
  flex:1;
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

/* small label under display */
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

.key {
  background: linear-gradient(180deg,#1b1c1e,#0f1011);
  border-radius:10px;
  padding: 12px 6px;
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

/* tighten streamlit spacing */
[data-testid="stVerticalBlock"] > div { gap:8px; }
</style>
""", unsafe_allow_html=True)

# ---------------- Safe math environment and wrappers ----------------

# Trig wrappers: when in DEG mode convert degrees -> radians for sin/cos/tan,
# and inverse trig returns degrees if DEG mode.
def sin_wr(x):
    x = float(x)
    if st.session_state.angle_mode == "DEG":
        return math.sin(math.radians(x))
    return math.sin(x)

def cos_wr(x):
    x = float(x)
    if st.session_state.angle_mode == "DEG":
        return math.cos(math.radians(x))
    return math.cos(x)

def tan_wr(x):
    x = float(x)
    if st.session_state.angle_mode == "DEG":
        return math.tan(math.radians(x))
    return math.tan(x)

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
    "log": math.log,      # natural
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

# ---------------- Helpers ----------------
def append(tok: str):
    st.session_state.expr = (st.session_state.expr or "") + str(tok)

def replace_factorials(expr: str) -> str:
    # replace number! -> factorial(number), and (expr)! -> factorial(expr)
    expr = re.sub(r"(\d+(?:\.\d+)?)!", r"factorial(\1)", expr)
    expr = re.sub(r"(\))!", r"factorial\1", expr)
    return expr

def safe_eval(expr: str):
    expr = expr.replace("^", "**")
    expr = replace_factorials(expr)
    # block accidental builtins
    return eval(expr, {"__builtins__": None}, SAFE)

def evaluate_expression():
    if not st.session_state.expr:
        return
    try:
        res = safe_eval(st.session_state.expr)
        st.session_state.last = str(res)
        st.session_state.expr = str(res)
    except Exception:
        st.error("Invalid expression")

# ---------------- Layout ----------------
st.markdown('<div class="calc-card">', unsafe_allow_html=True)

# Top: display row with two equal blocks (input / result)
st.markdown('<div class="display-row">', unsafe_allow_html=True)

# Left: input block
input_val = st.session_state.expr if st.session_state.expr else ""
st.markdown(f'<div class="display-block" id="input_block">{st.session_state.expr or ""}</div>', unsafe_allow_html=True)

# Right: result block — show last or 0
result_val = st.session_state.last if st.session_state.last else ""
st.markdown(f'<div class="display-block" id="result_block">{st.session_state.last or ""}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# sub info (angle, memory, shift state)
st.markdown(f'<div class="display-sub">Angle: {st.session_state.angle_mode} &nbsp;&nbsp; Memory: {st.session_state.memory} &nbsp;&nbsp; SHIFT: {"ON" if st.session_state.shift else "OFF"}</div>', unsafe_allow_html=True)

# ------- Buttons area -------
# We'll place main keys in a wide column and extras on the right side
col_keys, col_side = st.columns([9, 3])

with col_keys:
    # Scientific function rows (6 columns)
    st.markdown('<div class="keys grid-6">', unsafe_allow_html=True)
    c = st.columns(6)
    # SHIFT functional behavior: when SHIFT ON, primary trig -> inverse trig, etc.
    if c[0].button("sin", key="sin_btn"):
        append("asin(") if st.session_state.shift else append("sin(")
        st.session_state.shift = False
    if c[1].button("cos", key="cos_btn"):
        append("acos(") if st.session_state.shift else append("cos(")
        st.session_state.shift = False
    if c[2].button("tan", key="tan_btn"):
        append("atan(") if st.session_state.shift else append("tan(")
        st.session_state.shift = False
    if c[3].button("SHIFT", key="shift_btn"):
        # toggle shift mode
        st.session_state.shift = not st.session_state.shift
    if c[4].button("(", key="lpar_btn"):
        append("(")
    if c[5].button(")", key="rpar_btn"):
        append(")")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="keys grid-6">', unsafe_allow_html=True)
    c = st.columns(6)
    if c[0].button("ln", key="ln_btn"): append("ln(")
    if c[1].button("log", key="log_btn"): append("log10(")  # keep label 'log' for log10 as in many calculators
    if c[2].button("sqrt", key="sqrt_btn"): append("sqrt(")
    if c[3].button("x^2", key="x2_btn"): append("**2")
    if c[4].button("x^3", key="x3_btn"): append("**3")
    if c[5].button("x^y", key="xy_btn"): append("**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="keys grid-6">', unsafe_allow_html=True)
    c = st.columns(6)
    if c[0].button("pi", key="pi_btn"): append("pi")
    if c[1].button("e", key="e_btn"): append("e")
    if c[2].button("!", key="fact_btn"): append("!")   # will be converted
    if c[3].button("Ans", key="ans_btn"): append(st.session_state.last or "")
    if c[4].button("^", key="caret_btn"): append("**")
    if c[5].button("Exp", key="exp_btn"): append("exp(")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # Numeric keypad & operators (4 columns)
    st.markdown('<div class="keys grid-4">', unsafe_allow_html=True)
    k = st.columns(4)
    if k[0].button("7", key="k7"): append("7")
    if k[1].button("8", key="k8"): append("8")
    if k[2].button("9", key="k9"): append("9")
    if k[3].button("/", key="kdiv"): append("/")
    k = st.columns(4)
    if k[0].button("4", key="k4"): append("4")
    if k[1].button("5", key="k5"): append("5")
    if k[2].button("6", key="k6"): append("6")
    if k[3].button("*", key="kmul"): append("*")
    k = st.columns(4)
    if k[0].button("1", key="k1"): append("1")
    if k[1].button("2", key="k2"): append("2")
    if k[2].button("3", key="k3"): append("3")
    if k[3].button("-", key="ksub"): append("-")
    k = st.columns(4)
    if k[0].button("0", key="k0"): append("0")
    if k[1].button(".", key="kdot"): append(".")
    if k[2].button("+/-", key="kneg"):
        # toggle sign for current expr or last
        expr = st.session_state.expr or st.session_state.last or ""
        if expr.startswith("-"):
            st.session_state.expr = expr[1:]
        else:
            st.session_state.expr = "-" + expr
    if k[3].button("+", key="kadd"): append("+")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Action row: DEL / AC / = / Mode
    a1, a2, a3, a4 = st.columns([2,2,2,4])
    if a1.button("DEL", key="del_btn"): st.session_state.expr = (st.session_state.expr or "")[:-1]
    if a2.button("AC", key="ac_btn"):
        st.session_state.expr = ""
        st.session_state.last = ""
    if a3.button("=", key="eq_btn"):
        evaluate_expression()
    if a4.button("Mode: DEG/RAD", key="mode_btn"):
        st.session_state.angle_mode = "RAD" if st.session_state.angle_mode == "DEG" else "DEG"

with col_side:
    st.markdown('<div class="side-panel">', unsafe_allow_html=True)
    st.subheader("Memory & Extras")
    if st.button("M+", key="mplus"):
        try:
            st.session_state.memory += float(st.session_state.last)
            st.success("Added to memory")
        except Exception:
            st.error("No numeric last answer")
    if st.button("M-", key="mminus"):
        try:
            st.session_state.memory -= float(st.session_state.last)
            st.success("Subtracted from memory")
        except Exception:
            st.error("No numeric last answer")
    if st.button("MR", key="mrec"): st.session_state.expr = (st.session_state.expr or "") + str(st.session_state.memory)
    if st.button("MC", key="mclear"): st.session_state.memory = 0.0

    st.markdown("---")
    st.markdown("**Quick tips**")
    st.markdown("- Use `^` for power (becomes `**`).")
    st.markdown("- Use `!` for factorial (auto-converted).")
    st.markdown("- SHIFT toggles inverse trig when ON (press SHIFT then the trig key).")
    st.markdown("- Trig obeys DEG/RAD mode shown above.")
    st.markdown("</div>", unsafe_allow_html=True)

# footer: small caption
st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
st.caption("fx-991 inspired — visual & layout inspiration only")
