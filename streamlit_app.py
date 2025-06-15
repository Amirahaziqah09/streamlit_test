import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests

# ----------------------------
# Title
# ----------------------------
st.title("💰 Personal Finance Tracker")

# ----------------------------
# Initialize session state
# ----------------------------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["Date", "Category", "Type", "Amount"])

# ----------------------------
# Input form
# ----------------------------
with st.form("entry_form", clear_on_submit=True):
    st.subheader("Add Transaction")
    date = st.date_input("Date", datetime.date.today())
    category = st.text_input("Category")
    trans_type = st.radio("Type", ["Income", "Expense"], horizontal=True)
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button
