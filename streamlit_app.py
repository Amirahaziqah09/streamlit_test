import streamlit as st
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt

# Title of Streamlit App
st.title("Personal Finance Tracker")

# File CSV to store data
FILE = "finance_data.csv"

# Loading data if CSV exists
try:
    df = pd.read_csv(FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Description", "Amount", "Type", "Date"])

# Input for adding new entry
st.sidebar.header("Add new entry")
description = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount", min_value=0.0)
entry_type = st.sidebar.selectbox("Type", ["Income", "Expense"])
entry_date = st.sidebar.date_input("Date", datetime.date.today())    

if st.sidebar.button("Add entry"):
    new = pd.DataFrame([{
        "Description": description,
        "Amount": amount,
        "Type": entry_type,
        "Date": entry_date
    }])
    df = pd.concat([df, new], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("Entry successfully added!")

# Display the data
st.subheader("All Transactions")
st.dataframe(df)

# Summary
st.subheader("Summary")
total_income = df.loc[df.Type == "Income", "Amount"].sum()
total_expense = df.loc[df.Type == "Expense", "Amount"].sum()
net_saving = total_income - total_expense

st.write(f"Total Income: RM{total_income:.2f}")
st.write(f"Total Expenses: RM{total_expense:.2f}")
st.write(f"Net Saving: RM{net_saving:.2f}")

# Set Monthly Budget
st.sidebar.number_input("Set Monthly Budget (RM)", min_value=0.0, key='budget')
budget = st.session_state.budget

st.write(f"Monthly Budget: RM{budget:.2f}")

if total_expense > budget:
    st.error("Alert: Expenses have exceeded your budget!")

# Currency Conversion
st.sidebar.header("Currency Conversion")
currency = st.sidebar.text_input("Target Currency (e.g. USD)", "USD")

if st.sidebar.button("Convert to " + currency):
    try:
        response = requests.get(f"https://api.exchangerate.host/convert?from=MYR&to={currency}")
        rate = response.json()["result"]
        st.success(f"1 MYR = {rate} {currency}")

        st.write(f"Total Income in {currency}: {total_income * rate:.2f}")
        st.write(f"Total Expenses in {currency}: {total_expense * rate:.2f}")

    except Exception as e:
        st.error("Currency conversion failed. Please try again later.")
        st.error(e)


# Charts
st.subheader("Visualization")
if not df.empty:
    pie_data = df.groupby("Type")["Amount"].sum()
    st.pie(pie_data,labels=pie_data.index)

    st.bar_chart(df.groupby("Type")["Amount"].sum())    

# Export CSV
st.sidebar.download_button(
    label='Download CSV',
    data=df.to_csv(index=False),
    file_name='finance_data.csv',
    mime='text/csv'
)
