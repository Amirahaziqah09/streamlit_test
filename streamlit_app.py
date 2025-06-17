import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Personal Finance Tracker", layout="centered")

st.title("💰 Personal Finance Tracker")

# --- Session State for Transactions ---
if "transactions" not in st.session_state:
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
with st.form("transaction_form"):
    t_type = st.selectbox("Type", ["Income", "Expense"])
    category = st.text_input("Category")
    amount = st.number_input("Amount (RM)", min_value=0.01, format="%.2f")
    submitted = st.form_submit_button("Add")

    if submitted and category:
        st.session_state.transactions.append([t_type, category, amount])
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
    if from_currency == to_currency:
        st.info("Same currency selected. No conversion needed.")
    else:
        try:
            url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                converted = data["rates"][to_currency]
                st.success(f"{amount:.2f} {from_currency} = {converted:.2f} {to_currency}")
            else:
                st.error(f"API Error: {response.status_code}")

        except Exception as e:
            st.error(f"Connection failed: {e}")

# --- Transactions Table ---
st.subheader("📋 Transactions")
if df.empty:
    st.info("No transactions added yet.")
else:
    st.dataframe(df, use_container_width=True)

# Load saved transactions if CSV exists
import os

transaction_file = "transactions.csv"

if os.path.exists(transaction_file):
    st.session_state.transactions = pd.read_csv(transaction_file).values.tolist()

# --- CSV DOWNLOAD --- 
st.download_button(
    label='Download CSV',
    data=df.to_csv(index=False),
    file_name='transactions.csv',
    mime='text/csv'
)
