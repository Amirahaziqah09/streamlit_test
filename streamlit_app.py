import streamlit as st
import pandas as pd
from datetime import date

# Store data in CSV file
DATA_FILE = "finance_data.csv"

# Function to load or create data
@st.cache_data
def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["Date"])
    except:
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Note"])

# Function to save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# App title
st.title("📒 Simple Personal Finance Tracker")

# Load existing data
data = load_data()

# Input form
st.header("Add Transaction")
with st.form("transaction_form"):
    date_input = st.date_input("Date", date.today())
    trans_type = st.radio("Type", ["Income", "Expense"])
    amount = st.number_input("Amount (RM)", min_value=0.01, step=0.01)
    category = st.selectbox("Category", ["Salary", "Food", "Transport", "Other"])
    note = st.text_input("Note")
    submit = st.form_submit_button("Save")

    if submit:
        new_data = pd.DataFrame({
            "Date": [date_input],
            "Type": [trans_type],
            "Amount": [amount],
            "Category": [category],
            "Note": [note]
        })
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)
        st.success("Transaction saved successfully!")

# Display transactions
st.header("Transaction List")
if not data.empty:
    st.dataframe(data.sort_values("Date", ascending=False))
    total_income = data[data["Type"] == "Income"]["Amount"].sum()
    total_expense = data[data["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.metric("Total Income", f"RM {total_income:.2f}")
    st.metric("Total Expenses", f"RM {total_expense:.2f}")
    st.metric("Balance", f"RM {balance:.2f}")
else:
    st.info("No transactions yet. Add some above.")
