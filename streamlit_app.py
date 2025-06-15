# personal_finance_tracker/app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests

st.set_page_config(page_title="Simple Finance App", layout="centered")

st.title("🧾 Simple Daily Finance Logger")

# Load existing data
@st.cache_data
def load_data():
    try:
        return pd.read_csv("finance_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount"])

data = load_data()

# Add new transaction
st.header("➕ Add New Transaction")
with st.form("new_transaction"):
    date = st.date_input("Date", value=datetime.today())
    trans_type = st.radio("Transaction Type", ["Income", "Expense"], horizontal=True)
    category = st.text_input("Category", placeholder="e.g. Salary, Food, Transport")
    amount = st.number_input("Amount (MYR)", min_value=0.0, step=0.01, format="%.2f")
    add = st.form_submit_button("Add Transaction")

if add:
    new_row = pd.DataFrame({"Date": [date], "Type": [trans_type], "Category": [category], "Amount": [amount]})
    data = pd.concat([data, new_row], ignore_index=True)
    data.to_csv("finance_data.csv", index=False)
    st.success("Transaction added!")

# Show transaction history
st.header("📋 Transaction History")
if not data.empty:
    st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.info("No transactions recorded yet.")

# Show summary charts
if not data.empty:
    st.header("📊 Summary Charts")
    data["Date"] = pd.to_datetime(data["Date"])
    summary = data.groupby(["Date", "Type"])["Amount"].sum().unstack().fillna(0)
    summary["Net"] = summary.get("Income", 0) - summary.get("Expense", 0)
    summary["Balance"] = summary["Net"].cumsum()

    st.subheader("💹 Daily Net Balance")
    st.line_chart(summary["Balance"])

    st.subheader("🧮 Income vs Expenses")
    total_income = data[data["Type"] == "Income"]["Amount"].sum()
    total_expense = data[data["Type"] == "Expense"]["Amount"].sum()
    fig, ax = plt.subplots()
    ax.bar(["Income", "Expense"], [total_income, total_expense], color=["green", "red"])
    ax.set_ylabel("Amount (MYR)")
    st.pyplot(fig)

# Show exchange rates
st.header("🌍 Live Exchange Rates (MYR)")
try:
    response = requests.get("https://api.exchangerate-api.com/v4/latest/MYR")
    rates = response.json()["rates"]
    selected = st.multiselect("Select currencies to view: ", ["USD", "EUR", "GBP", "SGD", "JPY"])
    if selected:
        for currency in selected:
            st.write(f"1 MYR = {rates[currency]:.4f} {currency}")
except:
    st.error("Unable to fetch exchange rates. Please check your internet connection or API status.")
