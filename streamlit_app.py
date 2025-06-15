# personal_finance_tracker/app.py

import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt  # ✅ Needed for pie chart
import requests
from datetime import datetime

st.set_page_config(page_title="Personal Finance Tracker", layout="centered")
st.title("💸 Personal Finance Tracker")
st.write("Track your daily income and expenses.")

# Function to load transaction data from CSV
def load_data():
    try:
        df = pd.read_csv("data.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # ✅ Ensure proper datetime format
        return df
    except:
        return pd.DataFrame(columns=["Date", "Category", "Type", "Amount"])

data = load_data()

# ------------------------------
# 🚀 Input Form for Transactions
# ------------------------------
with st.form("Add Transaction"):
    date = st.date_input("Date", datetime.now())
    category = st.selectbox("Category", ["Food", "Transport", "Salary", "Others"])
    trans_type = st.radio("Type", ["Income", "Expense"])
    amount = st.number_input("Amount (MYR)", min_value=0.01, format="%.2f")  # ✅ Prevent zero entries
    submitted = st.form_submit_button("Save")

if submitted:
    new_data = pd.DataFrame({
        "Date": [date],
        "Category": [category],
        "Type": [trans_type],
        "Amount": [amount]
    })
    data = pd.concat([data, new_data], ignore_index=True)
    data.to_csv("data.csv", index=False)
    st.success("✅ Transaction saved successfully!")

# ------------------------------
# 📊 Transaction Summary Table
# ------------------------------
st.subheader("📊 Transaction Summary")
if "Date" in data.columns:
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    st.dataframe(data.sort_values(by="Date", ascending=False))
else:
    st.warning("No 'Date' column found. Please check your data.")

# ------------------------------
# 📈 Data Visualizations
# ------------------------------
if not data.empty:
    expenses = data[data["Type"] == "Expense"]
    income = data[data["Type"] == "Income"]

    # 🎈 Pie Chart: Expense by Category
    if not expenses.empty:
        st.subheader("🎈 Expense Pie Chart by Category")
        pie_data = expenses.groupby("Category")["Amount"].sum()
        #fig1, ax1 = plt.subplots()
        ax1.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
    else:
        st.info("No expense data to display in pie chart.")

    # 📉 Line Chart: Cumulative Balance Over Time
    st.subheader("📉 Daily Cumulative Balance")
    grouped = data.groupby(["Date", "Type"])["Amount"].sum().unstack().fillna(0)
    grouped["Balance"] = grouped.get("Income", 0) - grouped.get("Expense", 0)
    grouped["Cumulative Balance"] = grouped["Balance"].cumsum()
    st.line_chart(grouped["Cumulative Balance"])

# ------------------------------
# 🌐 Currency Conversion (API)
# ------------------------------
st.subheader("🌐 Currency Conversion (via API)")

currency_choice = st.selectbox("Convert MYR to:", ["USD", "EUR", "SGD"])
myr_amount = st.number_input("Amount in MYR:", min_value=0.01, format="%.2f")

if st.button("Convert"):
    try:
        resp = requests.get("https://api.exchangerate-api.com/v4/latest/MYR")
        resp.raise_for_status()
        rates = resp.json()["rates"]
        if currency_choice in rates:
            converted = myr_amount * rates[currency_choice]
            st.success(f"💱 RM{myr_amount:.2f} = {converted:.2f} {currency_choice}")
        else:
            st.error("Selected currency not available in API response.")
    except Exception as e:
        st.error(f"API request failed: {e}")

