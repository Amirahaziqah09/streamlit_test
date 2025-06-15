import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests

# -----------------------------
# Page title
# -----------------------------
st.set_page_config(page_title="Personal Finance Tracker", layout="centered")
st.title("📊 Personal Finance Tracker")
st.markdown("Track your income & expenses, view charts, and get financial tips!")

# -----------------------------
# Initialize session state
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Date", "Category", "Type", "Amount"])

# -----------------------------
# Add transaction form
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
# Display Data
# -----------------------------
if not st.session_state.data.empty:
    df = st.session_state.data
    df["Date"] = pd.to_datetime(df["Date"])
    st.subheader("📋 Transaction History")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

    # -----------------------------
    # Summary Stats
    # -----------------------------
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.metric("💵 Total Income", f"RM {total_income:,.2f}")
    st.metric("💸 Total Expenses", f"RM {total_expense:,.2f}")
    st.metric("🧮 Balance", f"RM {balance:,.2f}")

    # -----------------------------
    # Pie Chart: Income vs Expense
    # -----------------------------
    st.subheader("📈 Spending Breakdown")
    pie_data = df.groupby("Type")["Amount"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

    # -----------------------------
    # Line Chart: Spending Over Time
    # -----------------------------
    st.subheader("📅 Spending Over Time")
    expense_df = df[df["Type"] == "Expense"]
    line_data = expense_df.groupby("Date")["Amount"].sum().reset_index()
    st.line_chart(line_data.rename(columns={"Amount": "Expenses"}), x="Date", y="Expenses")

# -----------------------------
# Financial Tip (API Integration)
# -----------------------------
st.subheader("💡 Financial Tip of the Day")

try:
    advice = requests.get("https://api.adviceslip.com/advice").json()
    st.info(f"💬 {advice['slip']['advice']}")
except:
    st.warning("Could not fetch tip. Check your internet connection.")

# -----------------------------
# Save to CSV (optional)
# -----------------------------
st.markdown("💾 Want to save your data?")
if st.button("Download as CSV"):
    st.download_button("Click to Download", st.session_state.data.to_csv(index=False), file_name="finance_data.csv", mime="text/csv")
