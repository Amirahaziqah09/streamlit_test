# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Title of the App
st.title("Personal Finance Tracker")

# File to store transactions
FILE = "transactions.csv"


# Initialize CSV if it doesn't exist
def init_file():
    try:
        df = pd.read_csv(FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Description", "Type", "Amount"])
        df.to_csv(FILE, index=False)


# Loading data
def load_data():
    df = pd.read_csv(FILE)
    return df


# Saving data
def save_data(df):
    df.to_csv(FILE, index=False)


# Currency conversion
def convert_currency(amount, from_curr='MYR', to_curr='USD'):
    try:
        response = requests.get(f"https://api.exchangerate.host/convert?from={from_curr}&to={to_curr}&amount={amount}")
        return response.json()["result"]
    except Exception as e:
        st.error(f"Currency conversion failed: {e}")


# Initialize
init_file()
df = load_data()


# --- SIDEBAR --- 
st.sidebar.header("Add Transactions")
with st.sidebar.form("transaction_form"):
    description = st.text_input("Description")
    trans_type = st.selectbox("Type", ("Income", "Expense"))
    amount = st.number_input("Amount", min_value=0.0, format='%.2f')
    submitted = st.form_submit_button("Add")
    if submitted and description and amount > 0:
        new = pd.DataFrame([{
            "Description": description,
            "Type": trans_type,
            "Amount": amount
        }])
        df = pd.concat([df, new], ignore_index=True)
        save_data(df)
        st.success("Transaction successfully added!")


# --- MAIN --- 
st.subheader("Summary")

total_income = df.loc[df.Type == "Income", "Amount"].sum()
total_expense = df.loc[df.Type == "Expense", "Amount"].sum()
net_saving = total_income - total_expense

st.write(f"✅ **Total Income:** {total_income}")
st.write(f"❌ **Total Expenses:** {total_expense}")
st.write(f"💵 **Net Saving:** {net_saving}")

# Currency Conversion
st.subheader("Currency Conversion")
amount = st.number_input("Enter amount to convert")
from_curr = st.text_input("From (Default MYR)", "MYR")
to_curr = st.text_input("To (Default USD)", "USD")

if st.button("Convert Currency") and amount > 0:
    converted = convert_currency(amount, from_curr, to_curr)
    st.success(f"{amount} {from_curr} = {converted:.2f} {to_curr}")

# --- VISUALIZATION --- 
st.subheader("Visualization")

if not df.empty:
    df_group = df.groupby("Type")["Amount"].sum()

    # Pie Chart
    st.write("Distribution by Type")
    st.pyplot(df_group.plot.pie(autopct='%1.1f%%').figure)

    # Bar Chart
    st.write("Summary by Type")
    st.bar_chart(df_group)


# --- DATA --- 
st.subheader("All Transactions")
st.dataframe(df)


# --- CSV DOWNLOAD --- 
st.download_button(
    label='Download CSV',
    data=df.to_csv(index=False),
    file_name='transactions.csv',
    mime='text/csv'
)
