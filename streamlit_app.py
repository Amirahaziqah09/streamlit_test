import streamlit as st
import pandas as pd
import datetime

# Title of Streamlit App
st.title("Personal Finance Tracker")

# File CSV to store data
FILE = "finance_data.csv"

# Loading data if CSV exists
try:
    df = pd.read_csv(FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Note"])

# Input for adding new entry
st.subheader("Add Transaction")

# Date picker
transaction_date = st.date_input("Date", datetime.date.today())    

# Type (Income or Expense)
transaction_type = st.radio("Type", ["Income", "Expense"])

# Amount (with number picker)
transaction_amount = st.number_input("Amount (RM)", min_value=0.0, format="%.2f")

# Category (dropdown)
transaction_category = st.selectbox("Category", ["General", "Food", "Transport", "Shopping"])

# Note (text input)
transaction_note = st.text_input("Note")

# Save button
if st.button("Save"):
    new = pd.DataFrame([{
        "Date": transaction_date,
        "Type": transaction_type,
        "Amount": transaction_amount,
        "Category": transaction_category,
        "Note": transaction_note
    }])
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("Transaction saved successfully!")

# Display the data
st.subheader("Transaction List")
st.dataframe(df)

# Summary
st.subheader("Summary")
total_income = df.loc[df.Type == "Income", "Amount"].sum()
total_expense = df.loc[df.Type == "Expense", "Amount"].sum()
net_saving = total_income - total_expense

st.write(f"Total Income: RM{total_income:.2f}")
st.write(f"Total Expenses: RM{total_expense:.2f}")
st.write(f"Balance: RM{net_saving:.2f}")

