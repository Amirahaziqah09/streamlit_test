import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(page_title="Personal Finance Tracker", layout="centered")
st.title("📊 Personal Finance Tracker")
st.markdown("Track your income & expenses, view charts, convert currencies, and get financial tips!")

# -----------------------------
# Session State Initialization
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Date", "Category", "Type", "Amount"])

# -----------------------------
# Add Transaction Form
# -----------------------------
with st.form("transaction_form", clear_on_submit=True):
    st.subheader("➕ Add a Transaction")
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date", value=datetime.date.today())
        amount = st.number_input("Amount (MYR)", min_value=0.01, format="%.2f")

    with col2:
        category = st.text_input("Category (e.g., Food, Salary)")
        trans_type = st.selectbox("Type", ["Income", "Expense"])

    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        if not category:
            st.warning("Please enter a category.")
        else:
            new_data = pd.DataFrame([[date, category, trans_type, amount]],
                                    columns=["Date", "Category", "Type", "Amount"])
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
            st.success("Transaction added successfully!")

# -----------------------------
# Display Transaction History
# -----------------------------
if not st.session_state.data.empty:
    df = st.session_state.data
    df["Date"] = pd.to_datetime(df["Date"])
    st.subheader("📋 Transaction History")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

    # Summary Metrics
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.metric("💵 Total Income", f"RM {total_income:,.2f}")
    st.metric("💸 Total Expenses", f"RM {total_expense:,.2f}")
    st.metric("🧮 Balance", f"RM {balance:,.2f}")

    # -----------------------------
    # Pie Chart: Income vs Expense
    # -----------------------------
    st.subheader("📊 Spending Breakdown")
    pie_data = df.groupby("Type")["Amount"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

    # -----------------------------
    # Line Chart: Expenses Over Time
    # -----------------------------
    st.subheader("📈 Expenses Over Time")
    expense_df = df[df["Type"] == "Expense"]
    if not expense_df.empty:
        line_data = expense_df.groupby("Date")["Amount"].sum().reset_index()
        st.line_chart(line_data.rename(columns={"Amount": "Expenses"}), x="Date", y="Expenses")
    else:
        st.info("No expense data to display.")

# -----------------------------
# Financial Advice API
# -----------------------------
st.subheader("💡 Financial Tip of the Day")
try:
    advice = requests.get("https://api.adviceslip.com/advice").json()
    st.info(f"💬 {advice['slip']['advice']}")
except:
    st.warning("Could not fetch financial advice. Please check your connection.")

# -----------------------------
# Currency Exchange Converter
# -----------------------------st.subheader("💱 Currency Exchange")

# Currency options
currency = st.selectbox(
    "Select currency to convert from MYR:",
    ["USD", "EUR", "SGD", "GBP", "JPY"]
)

# Input amount
amount_to_convert = st.number_input("Amount in MYR:", min_value=0.0, format="%.2f", key="convert_amount")

# Convert action
if st.button("Convert"):
    with st.spinner("Fetching exchange rate..."):
        try:
            url = f"https://api.exchangerate.host/latest?base=MYR&symbols={currency}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Check if 'rates' exists
            if "rates" in data and currency in data["rates"]:
                rate = data["rates"][currency]
                converted = amount_to_convert * rate
                date = data.get("date", "N/A")
                st.success(f"✅ 1 MYR = {rate:.4f} {currency} (as of {date})")
                st.info(f"💰 RM {amount_to_convert:.2f} ≈ {converted:.2f} {currency}")
            else:
                st.error("Exchange rate data not found in API response.")
                st.json(data)  # Show full response for debugging

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
    #added up until here

# -----------------------------
# Download CSV
# -----------------------------
st.subheader("💾 Download Your Data")
if st.button("Export CSV"):
    st.download_button("Click to Download", st.session_state.data.to_csv(index=False),
                       file_name="finance_data.csv", mime="text/csv")
