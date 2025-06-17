import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

# Page configuration
st.set_page_config(page_title="Personal Finance Tracker", layout="centered")

st.title("💰 Personal Finance Tracker")

# --- Session State Initialization ---
if "transactions" not in st.session_state:
    st.session_state.transactions = []

# --- Load Transactions from CSV ---
transaction_file = "transactions.csv"
if os.path.exists(transaction_file) and not st.session_state.transactions:
    st.session_state.transactions = pd.read_csv(transaction_file).values.tolist()

# --- Summary Section ---
st.subheader("📊 Summary")

df = pd.DataFrame(st.session_state.transactions, columns=["Type", "Category", "Amount"])
income = df[df["Type"] == "Income"]["Amount"].sum() if not df.empty else 0
expenses = df[df["Type"] == "Expense"]["Amount"].sum() if not df.empty else 0
balance = income - expenses

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"RM {income:.2f}")
col2.metric("Expenses", f"RM {expenses:.2f}")
col3.metric("Balance", f"RM {balance:.2f}")

# --- Add Transaction Section ---
st.subheader("➕ Add Transaction")
with st.form("transaction_form"):
    t_type = st.selectbox("Type", ["Income", "Expense"])
    category = st.text_input("Category")
    amount = st.number_input("Amount (RM)", min_value=0.01, format="%.2f")
    submitted = st.form_submit_button("Add")

    if submitted and category:
        st.session_state.transactions.append([t_type, category, amount])
        # Save to CSV
        df = pd.DataFrame(st.session_state.transactions, columns=["Type", "Category", "Amount"])
        df.to_csv(transaction_file, index=False)
        st.success("Transaction added!")

# --- Chart Sectio
