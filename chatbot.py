import streamlit as st
import requests
import re
import os

API_KEY = os.getenv("API_KEY", "lNgJRoYqq7cv8vopajcVGNRSNy2EFN9T")

COMPANY_SYMBOLS = {
    "microsoft": "MSFT",
    "apple": "AAPL",
    "tesla": "TSLA",
    "google": "GOOGL",
    "amazon": "AMZN",
    "meta": "META",
    "netflix": "NFLX",
    "nvidia": "NVDA",
    "intel": "INTC",
    "ibm": "IBM"
}

def extract_company_symbol(query):
    for name in COMPANY_SYMBOLS:
        if name in query.lower():
            return COMPANY_SYMBOLS[name]
    return "MSFT"

def extract_year(query):
    match = re.search(r"\b(20\d{2})\b", query)
    return match.group(1) if match else None

def get_income_statement(symbol):
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=5&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def real_chatbot(user_query):
    symbol = extract_company_symbol(user_query)
    year = extract_year(user_query)
    data_list = get_income_statement(symbol)

    if not data_list:
        return f"Unable to fetch financial data for {symbol}."

    data = None
    if year:
        for entry in data_list:
            if entry["calendarYear"] == year:
                data = entry
                break
    else:
        data = data_list[0]

    if not data:
        return f"No financial data available for {symbol} in {year}."

    query = user_query.lower()

    if "total revenue" in query:
        return f"The total revenue for {symbol} in {data['calendarYear']} is ${data['revenue'] / 1e9:.2f} billion."
    elif "net income" in query:
        return f"The net income for {symbol} in {data['calendarYear']} is ${data['netIncome'] / 1e9:.2f} billion."
    elif "operating income" in query:
        return f"The operating income for {symbol} in {data['calendarYear']} is ${data['operatingIncome'] / 1e9:.2f} billion."
    elif "r&d" in query or "research" in query:
        return f"R&D expenses for {symbol} in {data['calendarYear']} were ${data['researchAndDevelopmentExpenses'] / 1e9:.2f} billion."
    elif "eps" in query or "earnings per share" in query:
        return f"Earnings per share (EPS) for {symbol} in {data['calendarYear']} is ${data['eps']:.2f}."
    elif "cash flow" in query:
        return f"Cash flow from operating activities for {symbol} in {data['calendarYear']} is ${data['operatingCashFlow'] / 1e9:.2f} billion."
    else:
        return "Sorry, I can only answer specific questions like revenue, net income, R&D, EPS, or cash flow."

# Streamlit UI
st.title("💬 Financial Chatbot")

user_query = st.text_input("Ask a financial question (e.g., 'What was Apple's net income in 2022?')")

if st.button("Ask"):
    if user_query:
        answer = real_chatbot(user_query)
        st.success(answer)
    else:
        st.warning("Please enter a question.")
