import streamlit as st
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt
import altair as alt

# --- Constants ---
BASE_CURRENCY = "MYR"
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
API_URL = f"https://api.apilayer.com/exchangerates_data/latest?base={BASE_CURRENCY}"

# --- Load or Create Data ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data/finance_data.csv", parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Currency", "Category", "Description", "Converted"])


def save_data(df):
    df.to_csv("data/finance_data.csv", index=False)


# --- Fetch Exchange Rates ---
@st.cache_data(ttl=3600)
def get_exchange_rates():
    headers = {"apikey": API_KEY}
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()["rates"]
        else:
            st.warning("Currency API error: Using default rate of 1.0")
            return {}
    except:
        st.error("Failed to fetch exchange rates")
        return {}


# --- Convert Amount ---
def convert_to_base(amount, currency, rates):
    if currency == BASE_CURRENCY or not rates:
        return amount
    try:
        rate = rates[currency]
        return round(amount / rate, 2)
    except:
        return amount


# --- Main App ---
st.set_page_config(page_title="Personal Finance Tracker", layout="centered")
st.title("💰 Personal Finance Tracker")

# Load data
rates = get_exchange_rates()
data = load_data()

# --- Input Form ---
st.subheader("Add Transaction")
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    date = col1.date_input("Date", datetime.date.today())
    trans_type = col2.selectbox("Type", ["Income", "Expense"])

    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    currency = st.selectbox("Currency", [BASE_CURRENCY] + sorted(rates.keys()))

    category = st.selectbox("Category", ["Food", "Transport", "Salary", "Shopping", "Utilities", "Other"])
    description = st.text_input("Description")

    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        converted = convert_to_base(amount, currency, rates)
        new_entry = pd.DataFrame({
            "Date": [date],
            "Type": [trans_type],
            "Amount": [amount],
            "Currency": [currency],
            "Category": [category],
            "Description": [description],
            "Converted": [converted if trans_type == "Expense" else -converted]
        })
        data = pd.concat([data, new_entry], ignore_index=True)
        save_data(data)
        st.success("Transaction added successfully!")

# --- Visualizations ---
st.subheader("📊 Financial Overview")

if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"])

    # Total balance
    balance = data["Converted"].sum()
    st.metric("Current Balance (MYR)", f"RM {balance:.2f}")

    # Bar chart by category
    st.write("### Expenses by Category")
    expenses = data[data["Type"] == "Expense"]
    category_totals = expenses.groupby("Category")["Converted"].sum().reset_index()
    st.bar_chart(category_totals.set_index("Category"))

    # Line chart by month
    st.write("### Monthly Savings Trend")
    data["Month"] = data["Date"].dt.to_period("M").astype(str)
    monthly = data.groupby("Month")["Converted"].sum().cumsum().reset_index()
    line_chart = alt.Chart(monthly).mark_line(point=True).encode(
        x="Month", y="Converted"
    ).properties(width=600)
    st.altair_chart(line_chart)

    # Transaction Table
    st.write("### All Transactions")
    st.dataframe(data.sort_values("Date", ascending=False))
else:
    st.info("No data available. Please add transactions.")
