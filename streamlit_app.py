import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# App Title
st.set_page_config(page_title="💰 Personal Finance Tracker", layout="centered")
st.title("💼 Personal Finance Tracker")

# CSV File
FILE = "transactions.csv"

# Initialize CSV
def init_file():
    try:
        pd.read_csv(FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Description", "Type", "Category", "Amount"])
        df.to_csv(FILE, index=False)

# Load Data
def load_data():
    return pd.read_csv(FILE)

# Save Data
def save_data(df):
    df.to_csv(FILE, index=False)

# Convert Currency
def convert_currency(amount, from_curr='MYR', to_curr='USD'):
    try:
        url = f"https://api.exchangerate.host/convert?from={from_curr}&to={to_curr}&amount={amount}"
        response = requests.get(url)
        return response.json().get("result")
    except Exception as e:
        st.error(f"Currency conversion failed: {e}")
        return None

# Initialize
init_file()
df = load_data()

# --- SIDEBAR: Add Transaction ---
st.sidebar.header("➕ Add Transaction")
with st.sidebar.form("transaction_form"):
    date = st.date_input("Date", datetime.today())
    description = st.text_input("Description")
    trans_type = st.selectbox("Type", ["Income", "Expense"])
    category = st.text_input("Category (e.g. Food, Salary, Bills)")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add")
    
    if submitted and description and amount > 0:
        new = pd.DataFrame([{
            "Date": date,
            "Description": description,
            "Type": trans_type,
            "Category": category,
            "Amount": amount
        }])
        df = pd.concat([df, new], ignore_index=True)
        save_data(df)
        df = load_data()
        st.sidebar.success("Transaction added ✅")

# --- SUMMARY ---
st.subheader("📊 Summary")

total_income = df[df.Type == "Income"]["Amount"].sum()
total_expense = df[df.Type == "Expense"]["Amount"].sum()
net_saving = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"RM {total_income:.2f}")
col2.metric("Expenses", f"RM {total_expense:.2f}")
col3.metric("Net Saving", f"RM {net_saving:.2f}")

# --- Currency Converter ---
st.subheader("🌍 Currency Conversion")
conv_amt = st.number_input("Enter amount", key="convert")
from_curr = st.text_input("From Currency", "MYR")
to_curr = st.text_input("To Currency", "USD")

if st.button("Convert") and conv_amt > 0:
    result = convert_currency(conv_amt, from_curr, to_curr)
    if result:
        st.success(f"{conv_amt} {from_curr} = {result:.2f} {to_curr}")

# --- Filters ---
st.subheader("📅 Filter by Month (Optional)")
df["Date"] = pd.to_datetime(df["Date"])
month_option = st.selectbox("Select Month", options=["All"] + sorted(df["Date"].dt.strftime("%B %Y").unique()))

if month_option != "All":
    selected_month = pd.to_datetime(month_option)
    df = df[df["Date"].dt.strftime("%B %Y") == selected_month.strftime("%B %Y")]

# --- Visualization ---
if not df.empty:
    st.subheader("📈 Visualization")

    df_group = df.groupby("Type")["Amount"].sum()

    # Pie Chart
    st.write("Transaction Distribution")
    fig, ax = plt.subplots()
    df_group.plot.pie(autopct='%1.1f%%', ax=ax, startangle=90)
    ax.set_ylabel("")
    st.pyplot(fig)

    # Bar Chart by Category (for Expenses)
    st.write("Expenses by Category")
    cat_group = df[df.Type == "Expense"].groupby("Category")["Amount"].sum()
    st.bar_chart(cat_group)

# --- Data Table ---
st.subheader("📋 All Transactions")
st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

# --- Download CSV ---
st.download_button(
    label="📥 Download CSV",
    data=df.to_csv(index=False),
    file_name="transactions.csv",
    mime="text/csv"
)
