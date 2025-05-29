import streamlit as st
import requests

# Set the app title
st.title('Hai Hai !! 💱') 

# Add a welcome message
st.write('Welcome to my Streamlit app!') 

# Create a text input
widgetuser_input = st.text_input('Enter a custom message:', 'Hello, Streamlit!') 

# Display the customized message
st.write('Customized Message:', widgetuser_input)

# Currency options (you can expand this list as needed)
currencies = [
    'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'SGD'
]

# Currency dropdown
base_currency = st.selectbox('Select base currency:', currencies)

# API call
url = f'https://api.vatcomply.com/rates?base={base_currency}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    st.write(f'Exchange rates for {base_currency}:')
    st.json(data)
else:
    st.error(f"API call failed with status code: {response.status_code}")
