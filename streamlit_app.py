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
        pd.read_csv(FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Description", "Type", "Amount"])
        df.to_csv(FILE, index=False)

# Load data
def load_data():
    return pd.read_csv(FILE)

# Save data
def save_data(df):
    df.to_csv(FILE, index=False)

# Currency conversion
def convert_currency(amount, from_curr='MYR', to_curr='USD'):
    try:
        response = requests.get(
            f"https://api.exchangerate.host/convert?from={from_curr}&to={to_curr}&amount={amount}"
        )
        data = response.json()
        return data.get("result")
    except Exception as e:
        st.error(f"Currency conversion failed: {e}")
        return None

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
        df = load_data()  # Refresh after saving
        st.success("Transaction successfully added!")

# --- MAIN --- 
st.subheader("Summary")

total_income = df.loc[df.Type == "Income", "Amount"].sum()
total_expense = df.loc[df.Type == "Expense", "Amount"].sum()
net_saving = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("✅ Total Income", f"{total_income:.2f}")
col2.metric("❌ Total Expenses", f"{total_expense:.2f}")
col3.metric("💵 Net Saving", f"{net_saving:.2f}")

# Currency Conversion
st.subheader("Currency Conversion")
amount_conv = st.number_input("Enter amount to convert", key="conv_amount")
from_curr = st.text_input("From (Default MYR)", "MYR")
to_curr = st.text_input("To (Default USD)", "USD")

if st.button("Convert Currency") and amount_conv > 0:
    converted = convert_currency(amount_conv, from_curr, to_curr)
    if converted is not None:
        st.success(f"{amount_conv} {from_curr} = {converted:.2f} {to_curr}")

# --- VISUALIZATION --- 
st.subheader("Visualization")

if not df.empty:
    df_group = df.groupby("Type")["Amount"].sum()

    # Pie Chart
    st.write("Distribution by Type")
    fig, ax = plt.subplots()
    df_group.plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")  # Remove y-axis label for clarity
    st.pyplot(fig)

    # Bar Chart
    st.write("Summary by Type")
    st.bar_chart(df_group)

# --- DATA --- 
st.subheader("All Transactions")
st.dataframe(df)

# --- CSV DOWNLOAD --- 
st.download_button(
    label='📥 Download CSV',
    data=df.to_csv(index=False),
    file_name='transactions.csv',
    mime='text/csv'
)
