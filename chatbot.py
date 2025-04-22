from flask import Flask, render_template, request
import requests
import re

app = Flask(__name__)

API_KEY = "lNgJRoYqq7cv8vopajcVGNRSNy2EFN9T"

# Step 1: Map company names to stock symbols
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

# Step 2: Extract company symbol from user query
def extract_company_symbol(query):
    for name in COMPANY_SYMBOLS:
        if name in query.lower():
            return COMPANY_SYMBOLS[name]
    return "MSFT"  # default if not found

# Step 3: Extract year from user query
def extract_year(query):
    match = re.search(r"\b(20\d{2})\b", query)
    return match.group(1) if match else None

# Step 4: Fetch financial data
def get_income_statement(symbol):
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=5&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Step 5: Chatbot logic
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
        data = data_list[0]  # most recent

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

# Step 6: Web route
@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    if request.method == "POST":
        user_query = request.form["query"]
        response = real_chatbot(user_query)
    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)
