import pymongo
import requests
import json
from datetime import datetime
import argparse

# Connect to MongoDB
myclient = pymongo.MongoClient("mongodb+srv://<YOUR-USER-PASS-DB>.8sxqmos.mongodb.net/?retryWrites=true&w=majority")
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

# Collection for CPI
cpi_collection = mydb["cpi_collection"]

# Collection PPI
ppi_collection = mydb["ppi_collection"]

# Collection for IPI
ipi_collection = mydb["ipi_collection"]

# Collection for Fed Funds Rate
fedir_collection = mydb["fed_interest_rate"]

# Collection for GDP
gdp_collection = mydb["real_gdp"]

# Collection for Unemployment Rate
ur_collection = mydb["ur_collection"]

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

# --------------------- GOOGLE STOCK PRICE LOGIC ---------------------

# Define Alpha Vantage API endpoints and parameters
api_key = 'OT31A9F95WIFCEXS'
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

# ----------------- Balance Sheet Logic ------------------------

# Make API request and parse response JSON for balance sheet data
response_balance = requests.get(url_balance_sheet)
data_bs = json.loads(response_balance.text)['annualReports'][0]

# Insert balance sheet data into database
data_bs['symbol'] = symbol
data_bs['date'] = datetime.now()
balancecol.insert_one(data_bs)

# ---------------- Financial Statements Logic ------------------

# Define Alpha Vantage API endpoint and parameters for financial statements
fs_url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}'

# Make API request for financial statements and parse response JSON
fs_response = requests.get(fs_url)
data_fs = json.loads(fs_response.text)

# Insert financial statements data into MongoDB
data_fs['symbol'] = symbol
data_fs['date'] = datetime.now()
financialcol.insert_one(data_fs)

# ------------------ Logic for PE, EPS, etc ---------------------

# Define Alpha Vantage API endpoint and parameters for PE ratio
pe_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'

# Make API request for PE ratio and parse response JSON
pe_response = requests.get(pe_url)
data_pe = json.loads(pe_response.text)

# Insert PE ratio data into MongoDB
data_pe['symbol'] = symbol
data_pe['date'] = datetime.now()
pecol.insert_one(data_pe)

# -------------------- CPI LOGIC -----------------------

# set the BLS API endpoint URL
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# set the series ID for the CPI-U index (all items)
series_id = "CUUR0000SA0"

# get the current year and month
now = datetime.now()
year = now.year
month = now.month

# set the API request headers
headers = {"Content-Type": "application/json"}

# set the API request data
data = {
    "seriesid": [series_id],
    "startyear": str(year),
    "endyear": str(year),
    "startmonth": f"{month:02d}",
    "endmonth": f"{month:02d}",
}

# send the API request and retrieve the data
response = requests.post(url, headers=headers, json=data)
response_data = response.json()

# extract the CPI value from the response data
cpi_value = response_data["Results"]["series"][0]["data"][0]["value"]

# create a document to insert into the collection
data_cpi = {
    "date": datetime(year, month, 1),
    "cpi": float(cpi_value),
}

# insert the document into the collection
cpi_collection.insert_one(data_cpi)

# print a message to confirm insertion
print("Data inserted successfully!")

# -------------- PPI LOGIC --------------------

# set the BLS API endpoint URL
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# set the series ID for the PPI (Producer Price Index)
series_id = "PCU22112222112241"

# get the current year and month
now = datetime.now()
year = now.year
month = now.month

# set the API request headers
headers = {"Content-Type": "application/json"}

# set the API request data
data = {
    "seriesid": [series_id],
    "startyear": str(year),
    "endyear": str(year),
    "startmonth": f"{month:02d}",
    "endmonth": f"{month:02d}",
}

# send the API request and retrieve the data
response = requests.post(url, headers=headers, json=data)
response_data = response.json()

# extract the PPI value from the response data
ppi_value = response_data["Results"]["series"][0]["data"][0]["value"]

# create a document to insert into the collection
data_ppi = {
    "date": datetime(year, month, 1),
    "ppi": float(ppi_value),
}

# insert the document into the collection
ppi_collection.insert_one(data_ppi)

# print a message to confirm insertion
print("Data inserted successfully!")

# retrieve the latest PPI data from the collection
latest_ppi_data = ppi_collection.find().sort("date", -1).limit(1)[0]
print(f"Latest PPI value (as of {latest_ppi_data['date']:%Y-%m-%d}): {latest_ppi_data['ppi']}")

# ---------------- UR LOGIC ---------------------

# set the BLS API endpoint URL
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# set the series ID for the unemployment rate
series_id = "LNS14000000"

# get the current year and month
now = datetime.now()
year = now.year
month = now.month

# set the API request headers
headers = {"Content-Type": "application/json"}

# set the API request data
data = {
    "seriesid": [series_id],
    "startyear": str(year),
    "endyear": str(year),
    "startperiod": f"M{month}",
    "endperiod": f"M{month}",
}

# send the API request and retrieve the data
response = requests.post(url, headers=headers, json=data)
response_data = response.json()

# extract the unemployment rate value from the response data and convert to decimal
ur_value = float(response_data["Results"]["series"][0]["data"][0]["value"]) / 100

# create a document to insert into the collection
data_ur = {
    "date": datetime(year, month, 1),
    "ur": ur_value,
}

# insert the document into the collection
ur_collection.insert_one(data_ur)

# print a message to confirm insertion
print("Data inserted successfully!")

# retrieve the latest unemployment rate data from the collection
latest_ur_data = ur_collection.find().sort("date", -1).limit(1)[0]
print(f"Latest unemployment rate (as of {latest_ur_data['date']:%Y-%m-%d}): {latest_ur_data['ur']}%")

# --------------- FEDIR LOGIC --------------------

# set the Alpha Vantage API endpoint URL
url = "https://www.alphavantage.co/query"

# set the API request parameters
# KIM THIS IS FOR ALPHA VANTAGE
params = {
    "function": "FEDERAL_FUNDS_RATE",
    "apikey": "<YOUR-KEY-HERE>",
}

# send the API request and retrieve the data
response = requests.get(url, params=params)
response_data = response.json()

# print the entire response
print(response_data)

# extract the latest monthly interest rate value from the response data
data = response_data["data"]
latest_month = data[0]["date"][:-3]
interest_rate = float(data[0]["value"])

# insert the latest monthly interest rate into the collection
fedir_collection.insert_one({
    "date": latest_month,
    "rate": interest_rate,
})

# print a message to confirm insertion
print("Data inserted successfully!")

# retrieve the latest interest rate data from the collection
latest_interest_rate = fedir_collection.find().sort("date", -1).limit(1)[0]
print(f"Latest interest rate (as of {latest_interest_rate['date']}): {latest_interest_rate['rate']}%")

# ------------------ IPI LOGIC ----------------------

# set the BLS API endpoint URL
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# set the series ID for the Industrial Production Index
series_id = "EIUIR"

# get the current year and month
now = datetime.now()
current_year = str(now.year)
current_month = now.strftime("%B").upper()

# set the API request data to only include the most recent month
data = {
    "seriesid": [series_id],
    "startyear": current_year,
    "endyear": current_year,
    "startperiod": current_month,
    "endperiod": current_month,
    "registrationkey": "<YOUR-KEY-HERE>"
}

# send the API request and retrieve the data
response = requests.post(url, json=data)
response_data = response.json()

# extract the IPI value from the response data
ipi_value = float(response_data["Results"]["series"][0]["data"][0]["value"])

# insert the data into the collection
ipi_collection.insert_one({
    "date": now,
    "value": ipi_value
})

# print a message to confirm insertion
print("Data inserted successfully!")

# retrieve the latest IPI data from the collection
latest_ipi_data = ipi_collection.find().sort("date", -1).limit(1)[0]
print(f"Latest IPI (as of {latest_ipi_data['date']:%B %Y}): {latest_ipi_data['value']}")


# -------------------- GDP LOGIC ------------------------

# set the Alpha Vantage API endpoint URL
url = "https://www.alphavantage.co/query"

# set the API request parameters
# KIM THIS IS FOR ALPHA VANTAGE 
params = {
    "function": "FEDERAL_FUNDS_RATE",
    "apikey": "<YOUR-KEY-HERE>",
}

# send the API request and retrieve the data
response = requests.get(url, params=params)
response_data = response.json()

# print the entire response
print(response_data)

# extract the latest monthly interest rate value from the response data
data = response_data["data"]
latest_month = data[0]["date"][:-3]
interest_rate = float(data[0]["value"])

# insert the latest monthly interest rate into the collection
gdp_collection.insert_one({
    "date": latest_month,
    "rate": interest_rate,
})

# print a message to confirm insertion
print("Data inserted successfully!")

# retrieve the latest interest rate data from the collection
latest_interest_rate = gdp_collection.find().sort("date", -1).limit(1)[0]
print(f"Latest interest rate (as of {latest_interest_rate['date']}): {latest_interest_rate['rate']}%")

