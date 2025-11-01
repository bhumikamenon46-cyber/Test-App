import streamlit as st

st.set_page_config(page_title="Simple Calculator", page_icon="🧮")

st.title("🧮 Normal Calculator")

# Inputs
num1 = st.number_input("Enter first number", value=0.0)
num2 = st.number_input("Enter second number", value=0.0)

operation = st.selectbox(
    "Select Operation",
    ["Add", "Subtract", "Multiply", "Divide"]
)

if st.button("Calculate"):
    if operation == "Add":
        result = num1 + num2
    elif operation == "Subtract":
        result = num1 - num2
    elif operation == "Multiply":
        result = num1 * num2
    elif operation == "Divide":
        if num2 == 0:
            st.error("Error: Cannot divide by zero!")
            result = None
        else:
            result = num1 / num2

    if result is not None:
        st.success(f"Result: {result}")
