import streamlit as st
import math

st.set_page_config(page_title="fx-991 Style Scientific Calculator", page_icon="🧮", layout="wide")
st.markdown("""
<style>
.calc-display {
    background-color: #E6E6E6;
    padding: 20px;
    font-size: 32px;
    font-weight: bold;
    border-radius: 12px;
    border: 2px solid #7d7d7d;
    text-align: right;
    color: black;
}
.button-big {
    border-radius: 10px;
    padding: 12px 0px;
    font-size:20px;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# --- Helper: safe eval environment ---
SAFE_NAMES = {
    # constants
    'pi': math.pi,
    'e': math.e,
    # math functions
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'log': math.log,      # natural log: log(x)
    'log10': math.log10,
    'sqrt': math.sqrt,
    'factorial': math.factorial,
    'abs': abs,
    'pow': pow,
    'exp': math.exp,
    'degrees': math.degrees,
    'radians': math.radians,
}

# initialize session state
if 'display' not in st.session_state:
    st.session_state.display = ''
if 'angle_mode' not in st.session_state:
    st.session_state.angle_mode = 'DEG'  # DEG or RAD
if 'memory' not in st.session_state:
    st.session_state.memory = 0.0

# --- UI Top area (Display + Mode row) ---
st.markdown("# fx-991 inspired — Streamlit Scientific Calculator")
cols = st.columns([3, 1, 1])
with cols[0]:
    st.markdown("#### Display")
    display_str = st.text_input("", value=st.session_state.display, key='display_input', label_visibility='collapsed')
with cols[1]:
    if st.button('MODE'):
        # toggle a simple mode placeholder (in real fx this opens a menu)
        st.info('Mode: COMP (calculator in computational mode)')
with cols[2]:
    if st.button('SHIFT'):
        st.info('Shift pressed — alternate functions available on some buttons')

# Keep session_state.display in sync with text input
st.session_state.display = display_str

st.markdown('---')

# --- Buttons layout inspired by fx-991MS ---
# We'll create left main area (buttons) and a slim right column for AC / DEL / = / Ans
left, right = st.columns([8, 2])

with right:
    if st.button('AC'):
        st.session_state.display = ''
    if st.button('DEL'):
        st.session_state.display = st.session_state.display[:-1]
    if st.button('Ans'):
        # append last answer if present
        try:
            last = st.session_state.get('last_answer', '')
            st.session_state.display += str(last)
        except Exception:
            pass
    if st.button('='):
        expr = st.session_state.display
        try:
            # replace factorial shorthand '!' if user typed it
            expr = expr.replace('^', '**')
            # handle degrees: if angle mode is DEG, wrap trig inputs
            # Simple approach: let user use deg() wrapper; provide quick conversion buttons below
            result = eval(expr, {'__builtins__': None}, SAFE_NAMES)
            st.session_state.last_answer = result
            st.success(f"= {result}")
            st.session_state.display = str(result)
        except Exception as e:
            st.error('Error: invalid expression')

with left:
    st.subheader('Function rows — scientific zone')
    # row 1
    r1 = st.columns(6)
    if r1[0].button('sin('):
        st.session_state.display += 'sin('
    if r1[1].button('cos('):
        st.session_state.display += 'cos('
    if r1[2].button('tan('):
        st.session_state.display += 'tan('
    if r1[3].button('^'):  # power
        st.session_state.display += '**'
    if r1[4].button('('):
        st.session_state.display += '('
    if r1[5].button(')'):
        st.session_state.display += ')'

    # row 2
    r2 = st.columns(6)
    if r2[0].button('asin('):
        st.session_state.display += 'asin('
    if r2[1].button('acos('):
        st.session_state.display += 'acos('
    if r2[2].button('atan('):
        st.session_state.display += 'atan('
    if r2[3].button('sqrt('):
        st.session_state.display += 'sqrt('
    if r2[4].button('x^2'):
        st.session_state.display += '**2'
    if r2[5].button('x^3'):
        st.session_state.display += '**3'

    # row 3
    r3 = st.columns(6)
    if r3[0].button('ln('):
        st.session_state.display += 'log('
    if r3[1].button('log10('):
        st.session_state.display += 'log10('
    if r3[2].button('e'):
        st.session_state.display += 'e'
    if r3[3].button('pi'):
        st.session_state.display += 'pi'
    if r3[4].button('!'):
        st.session_state.display += 'factorial('
    if r3[5].button('Exp'):
        st.session_state.display += 'exp('

    # row 4 — memory and angle
    r4 = st.columns(6)
    if r4[0].button('M+'):
        try:
            st.session_state.memory += float(st.session_state.get('last_answer', 0) or 0)
            st.success('Added to memory')
        except Exception:
            st.error('No numeric value to add')
    if r4[1].button('M-'):
        try:
            st.session_state.memory -= float(st.session_state.get('last_answer', 0) or 0)
            st.success('Subtracted from memory')
        except Exception:
            st.error('No numeric value to subtract')
    if r4[2].button('MR'):
        st.session_state.display += str(st.session_state.memory)
    if r4[3].button('MC'):
        st.session_state.memory = 0.0
    if r4[4].button('DEG'):
        st.session_state.angle_mode = 'DEG'
        st.info('Angle mode: DEG')
    if r4[5].button('RAD'):
        st.session_state.angle_mode = 'RAD'
        st.info('Angle mode: RAD')

    st.markdown('---')

    # numeric keypad layout (like calculator)
    keypad = [
        ['7', '8', '9', '/'],
        ['4', '5', '6', '*'],
        ['1', '2', '3', '-'],
        ['0', '.', 'Ans', '+']
    ]

    for row in keypad:
        cols_k = st.columns(len(row))
        for i, key in enumerate(row):
            if cols_k[i].button(key):
                if key == 'Ans':
                    st.session_state.display += str(st.session_state.get('last_answer', ''))
                else:
                    st.session_state.display += key

# --- Footer / usage hints ---
st.markdown('---')
st.write('**Usage tips:**')
st.write('- Use `^` for power (it will be converted to `**`).')
st.write('- Trig functions use radians by default in Python; switch to DEG/RAD to see info. When DEG is selected, convert angles using `radians(x)` or use the DEG button for convenience.')
st.write('- `!` button inserts `factorial(` — remember to close parenthesis and press `=`.')

st.caption('This UI is inspired by Casio fx-991 layout grouping (visual inspiration only).')
