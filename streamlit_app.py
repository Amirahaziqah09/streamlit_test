import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# CSV file name
FILE = "transactions.csv"

# Initialize CSV file
def init_file():
    try:
        pd.read_csv(FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Description", "Type", "Amount"])
        df.to_csv(FILE, index=False)

# Load and save data
def load_data():
    return pd.read_csv(FILE)

def save_data(df):
    df.to_csv(FILE, index=False)

# Currency converter function
def convert_currency(amount, from_curr="MYR", to_curr="USD"):
    try:
        url = f"https://api.exchangerate.host/convert?from={from_curr}&to={to_curr}&amount={amount}"
        response = requests.get(url)
        return response.json()["result"]
    except:
        return None

# Run the app
st.title("💰 Personal Finance Tracker")

# Initialize and load data
init_file()
df = load_data()

# Sidebar: Add transaction
st.sidebar.header("➕ Add Transaction")
with st.sidebar.form("form"):
    desc = st.text_input("Description")
    t_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Add")
    if submit and desc and amount > 0:
        new = pd.DataFrame([[desc, t_type, amount]], columns=["Description", "Type", "Amount"])
        df = pd.concat([df, new], ignore_index=True)
        save_data(df)
        st.sidebar.success("Transaction Added!")

# Summary
st.subheader("📊 Summary")
income = df[df.Type == "Income"]["Amount"].sum()
expense = df[df.Type == "Expense"]["Amount"].sum()
balance = income - expense

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"RM {income:.2f}")
col2.metric("Expenses", f"RM {expense:.2f}")
col3.metric("Balance", f"RM {balance:.2f}")

# Currency Conversion
st.subheader("🌍 Currency Converter")
amount_conv = st.number_input("Amount", key="convert")
from_curr = st.text_input("From", "MYR")
to_curr = st.text_input("To", "USD")
if st.button("Convert") and amount_conv > 0:
    result = convert_currency(amount_conv, from_curr, to_curr)
    if result:
        st.success(f"{amount_conv} {from_curr} = {result:.2f} {to_curr}")

# Visualization
if not df.empty:
    st.subheader("📈 Chart")
    group = df.groupby("Type")["Amount"].sum()
    fig, ax = plt.subplots()
    group.plot.pie(autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

# Show Data
st.subheader("📋 Transactions")
st.dataframe(df)

# CSV Download
st.download_button("Download CSV", data=df.to_csv(index=False), file_name="transactions.csv", mime="text/csv")
