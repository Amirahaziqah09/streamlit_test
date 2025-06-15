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

    
