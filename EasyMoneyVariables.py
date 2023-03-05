import pymongo
import requests
from datetime import datetime

# create a MongoClient instance
client = pymongo.MongoClient("mongodb+srv://sahilkhatra:easymoney*123@teameasymoney.8sxqmos.mongodb.net/?retryWrites=true&w=majority")

# select the database
db = client["TeamEasyMoney"]

# select the collection
cpi_collection = db["cpi_collection"]

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
cpi_data = {
    "date": datetime(year, month, 1),
    "cpi": float(cpi_value),
}

# insert the document into the collection
cpi_collection.insert_one(cpi_data)

# print a message to confirm insertion
print("Data inserted successfully!")
