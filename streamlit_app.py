import streamlit as st
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt
import altair as alt
import os

# --- Constants ---
BASE_CURRENCY = "MYR"
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
API_URL = f"https://api.apilayer.com/exchangerates_data/latest?base={BASE_CURRENCY}"
DATA_PATH = "finance_data.csv"

# --- Load or Create Data ---
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, parse_dates=["Date"])
    else:
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Currency", "Category", "Description", "Converted"])


def save_data(df):
    df.to_csv(DATA_PATH, index=False)


# --- Fetch Exchange Rates ---
@st.cache_data(ttl=3600)
def get_exchange_rates():
    headers = {"apikey": API_KEY}
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json().get("rates", {})
    except Exception as e:
        st.error(f"Exchange rate API error: {e}")
        return {}


# --- Convert Amount ---
def convert_to_base(amount, currency, rates):
    if currency == BASE_CURRENCY or not rates:
        return amount
    try:
        rate = rates.get(currency, 1.0)
        return round(amount / rate, 2)
    except:
        return amount


# --- Main App ---
st.set_page_config(page_title="Personal Finance Tracker", layout="centered")
st.title("📈 Personal Finance Tracker")

# Load data
rates = get_exchange_rates()
data = load_data()

# --- Input Form ---
st.subheader("➕ Add Transaction")
with st.form("entry_form"):
    date = st.date_input("Date", datetime.date.today())
    trans_type = st.radio("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    currency = st.selectbox("Currency", [BASE_CURRENCY] + sorted(rates.keys()))
    category = st.selectbox("Category", ["Food", "Transport", "Salary", "Shopping", "Utilities", "Other"])
    description = st.text_input("Description")
    submitted = st.form_submit_button("Add")

    if submitted:
        converted = convert_to_base(amount, currency, rates)
        signed_amount = -converted if trans_type == "Expense" else converted
        new_entry = pd.DataFrame({
            "Date": [date],
            "Type": [trans_type],
            "Amount": [amount],
            "Currency": [currency],
            "Category": [category],
            "Description": [description],
            "Converted": [signed_amount]
        })
        data = pd.concat([data, new_entry], ignore_index=True)
        save_data(data)
        st.success("Transaction added!")

# --- Visualizations ---
st.subheader("📊 Dashboard")

if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"])
    data["Month"] = data["Date"].dt.to_period("M").astype(str)

    # Balance
    balance = data["Converted"].sum()
    st.metric("Net Balance (MYR)", f"RM {balance:.2f}")

    # Expenses by Category
    expenses = data[data["Type"] == "Expense"]
    cat_totals = expenses.groupby("Category")["Converted"].sum().abs().reset_index()
    if not cat_totals.empty:
        st.write("### 📌 Expenses by Category")
        st.bar_chart(cat_totals.set_index("Category"))

    # Monthly Trend
    monthly_summary = data.groupby("Month")["Converted"].sum().reset_index()
    st.write("### 📅 Monthly Trend")
    trend_chart = alt.Chart(monthly_summary).mark_line(point=True).encode(
        x="Month", y="Converted"
    ).properties(width=600)
    st.altair_chart(trend_chart)

    # Transaction Table
    st.write("### 📄 All Transactions")
    st.dataframe(data.sort_values("Date", ascending=False))
else:
    st.info("No transactions yet. Start by adding some.")
