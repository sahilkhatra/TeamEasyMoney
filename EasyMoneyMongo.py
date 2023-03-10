import pymongo
import requests
import json
from datetime import datetime
import argparse

# Connect to MongoDB
myclient = pymongo.MongoClient("mongodb+srv://sahilkhatra:easymoney*123@teameasymoney.8sxqmos.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["TeamEasyMoney"]

# Collection for User Data
mycol = mydb["Users"]

# Collection for Stock Data
stockcol = mydb["StockData"]

# Collection for Financial Statements
financialcol = mydb["FinancialStatements"]

# Collection for Balance Sheets
balancecol = mydb["BalanceSheets"]

# Collection for Unemployment Rate
unemploymentcol = mydb["UnemploymentRate"]

# Collection for PE Ratio
pecol = mydb["PERatio"]

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--username", help="Username for registration")
parser.add_argument("--password", help="Password for registration")
parser.add_argument("--email", help="Email for registration")
args = parser.parse_args()

# Validate user input
if args.username and mycol.find_one({"username": args.username}):
    print("Username already exists.")
    exit()
elif args.email and mycol.find_one({"email": args.email}):
    print("Email already exists.")
    exit()

# Insert user data into database
if args.username and args.password and args.email:
    mydict = {"username": args.username, "password": args.password, "email": args.email}
    x = mycol.insert_one(mydict)
    print("Registration successful.")

# Define Alpha Vantage API endpoints and parameters
api_key = 'YOUR-API-KEY-HERE'
symbol = 'GOOGL'
interval = '5min'
url_stock = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'
url_balance_sheet = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={api_key}'

# Make API request and parse response JSON for stock data
response_stock = requests.get(url_stock)
data_stock = json.loads(response_stock.text)['Time Series (5min)']

# Iterate over data and insert each record into MongoDB for stock data
for date, data_prices in data_stock.items():
    date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    data_prices['date'] = date_time
    data_prices['symbol'] = symbol
    stockcol.insert_one(data_prices)

# Make API request and parse response JSON for balance sheet data
response_balance = requests.get(url_balance_sheet)
data_bs = json.loads(response_balance.text)['annualReports'][0]

# Insert balance sheet data into database
data_bs['symbol'] = symbol
data_bs['date'] = datetime.now()
balancecol.insert_one(data_bs)

# Define Alpha Vantage API endpoint and parameters for financial statements
fs_url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}'

# Make API request for financial statements and parse response JSON
fs_response = requests.get(fs_url)
data_fs = json.loads(fs_response.text)

# Insert financial statements data into MongoDB
data_fs['symbol'] = symbol
data_fs['date'] = datetime.now()
financialcol.insert_one(data_fs)

# Define Alpha Vantage API endpoint and parameters for PE ratio
pe_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'

# Make API request for PE ratio and parse response JSON
pe_response = requests.get(pe_url)
data_pe = json.loads(pe_response.text)

# Insert PE ratio data into MongoDB
data_pe['symbol'] = symbol
data_pe['date'] = datetime.now()
pecol.insert_one(data_pe)
