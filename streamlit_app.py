import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

st.set_page_config(page_title="Personal Finance Tracker", layout="centered")
st.title("💰 Personal Finance Tracker")

# --- Load or Init Transactions ---
transaction_file = "transactions.csv"

if "transactions" not in st.session_state:
    if os.path.exists(transaction_file):
        st.session_state.transactions = pd.read_csv(transaction_file).values.tolist()
    else:
        st.session_state.transactions = []

# --- Summary ---
st.subheader("📊 Summary")

df = pd.DataFrame(st.session_state.transactions, columns=["Type", "Category", "Amount"])

income = df[df["Type"] == "Income"]["Amount"].sum() if not df.empty else 0
expenses = df[df["Type"] == "Expense"]["Amount"].sum() if not df.empty else 0
balance = income - expenses

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"RM {income:.2f}")
col2.metric("Expenses", f"RM {expenses:.2f}")
col3.metric("Balance", f"RM {balance:.2f}")

# --- Add Transaction ---
st.subheader("➕ Add Transaction")
with st.form("transaction_form", clear_on_submit=True):
    t_type = st.selectbox("Type", ["Income", "Expense"])
    category = st.text_input("Category")
    amount = st.number_input("Amount (RM)", min_value=0.01, format="%.2f")
    submitted = st.form_submit_button("Add")

    if submitted and category:
        st.session_state.transactions.append([t_type, category, amount])
        # Save to CSV immediately
        pd.DataFrame(st.session_state.transactions, columns=["Type", "Category", "Amount"]).to_csv(transaction_file, index=False)
        st.success("Transaction added!")

# --- Chart ---
if not df.empty:
    chart = df.groupby("Type")["Amount"].sum().reset_index()
    fig = px.pie(chart, values="Amount", names="Type", title="Income vs Expenses")
    st.plotly_chart(fig, use_container_width=True)

# --- Currency Converter ---
st.subheader("🌍 Currency Converter")

amount = st.number_input("Amount", value=100.00)
from_currency = st.selectbox("From", ["MYR", "USD", "EUR", "SGD"], index=0)
to_currency = st.selectbox("To", ["USD", "MYR", "EUR", "SGD"], index=1)

if st.button("Convert"):
    try:
        # Step 1: Convert from any currency ➜ EUR (free API)
        if from_currency == "EUR":
            eur_amount = amount
        else:
            response1 = requests.get(
                f"https://api.exchangerate.host/convert?amount={amount}&from={from_currency}&to=EUR",
                timeout=10
            )
            data1 = response1.json()
            eur_amount = data1["result"]

        # Step 2: Convert from EUR ➜ target currency (Fixer.io)
        access_key = "c391f647be92d7579f9b6102c87053a4"  # Replace with your real Fixer.io key
        response2 = requests.get(
            f"http://data.fixer.io/api/latest?access_key={access_key}&symbols={to_currency}",
            timeout=10
        )
        data2 = response2.json()

        if data2.get("success"):
            rate = data2["rates"][to_currency]
            final_amount = eur_amount * rate
            st.success(f"{amount:.2f} {from_currency} = {final_amount:.2f} {to_currency}")
            st.caption(f"💱 Rate: 1 EUR = {rate:.4f} {to_currency}")
        else:
            st.error("Fixer API failed.")
            st.write(data2)

    except Exception as e:
        st.error(f"Conversion error: {e}")

# --- Transactions Table ---
st.subheader("📋 Transactions")
if df.empty:
    st.info("No transactions added yet.")
else:
    st.dataframe(df, use_container_width=True)
