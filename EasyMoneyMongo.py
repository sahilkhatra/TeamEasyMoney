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

# Define Alpha Vantage API endpoint and parameters
api_key = 'OT31A9F95WIFCEXS'
symbol = 'GOOGL'
interval = '5min'
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'

# Make API request and parse response JSON
response = requests.get(url)
data = json.loads(response.text)['Time Series (5min)']

# Iterate over data and insert each record into MongoDB
for date, prices in data.items():
    date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    prices['date'] = date_time
    prices['symbol'] = symbol
    stockcol.insert_one(prices)

# Define Alpha Vantage API endpoint and parameters for financial statements
fs_url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}'

# Make API request for financial statements and parse response JSON
fs_response = requests.get(fs_url)
fs_data = json.loads(fs_response.text)

# Insert financial statements data into MongoDB
fs_data['symbol'] = symbol
fs_data['date'] = datetime.now()
financialcol.insert_one(fs_data)








