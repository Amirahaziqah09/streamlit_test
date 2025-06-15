# personal_finance_tracker/app.py
import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
import requests
from datetime import datetime

# Title
st.title("💸 Personal Finance Tracker")
st.write("Track your daily income and expenses.")

# Load or initialize data
def load_data():
    try:
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame(columns=["Date", "Category", "Type", "Amount"])

data = load_data()

# Input Form
with st.form("Add Transaction"):
    date = st.date_input("Date", datetime.now())
    category = st.selectbox("Category", ["Food", "Transport", "Salary", "Others"])
    trans_type = st.radio("Type", ["Income", "Expense"])
    amount = st.number_input("Amount (MYR)", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Save")

if submitted:
    new_data = pd.DataFrame({"Date": [date], "Category": [category], "Type": [trans_type], "Amount": [amount]})
    data = pd.concat([data, new_data], ignore_index=True)
    data.to_csv("data.csv", index=False)
    st.success("Transaction saved successfully!")

# Display Data
st.subheader("📊 Transaction Summary")
st.dataframe(data.sort_values(by="Date", ascending=False))

# Visualization
if not data.empty:
    expenses = data[data["Type"] == "Expense"]
    income = data[data["Type"] == "Income"]

    # Expense Pie Chart
    st.subheader("🎈 Expense Pie Chart by Category")
    pie_data = expenses.groupby("Category")["Amount"].sum()
    #fig1, ax1 = plt.subplots()
    ax1.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    # Line chart for daily balance
    st.subheader("Daily Balance")
    data["Date"] = pd.to_datetime(data["Date"])
    grouped = data.groupby(["Date", "Type"])["Amount"].sum().unstack().fillna(0)
    grouped["Balance"] = grouped.get("Income", 0) - grouped.get("Expense", 0)
    grouped["Cumulative Balance"] = grouped["Balance"].cumsum()

    st.line_chart(grouped["Cumulative Balance"])

# Currency Conversion
st.subheader("🌐 Currency Conversion (API)")
try:
    resp = requests.get("https://api.exchangerate-api.com/v4/latest/MYR")
    rates = resp.json()["rates"]
    currency_choice = st.selectbox("Convert to:", ["USD", "EUR", "SGD"])
    myr_amount = st.number_input("Amount in MYR:", min_value=0.0, format="%.2f")
    if st.button("Convert"):
        converted = myr_amount * rates[currency_choice]
        st.success(f"RM{myr_amount:.2f} = {converted:.2f} {currency_choice}")
except:
    st.error("Failed to access currency exchange API.")
