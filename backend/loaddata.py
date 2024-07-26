from pymongo import MongoClient
import json

# Load the data from the DB
client = MongoClient('localhost', 27017)
db = client['Tour']
collection = db['spots']

# Find all the documents
data = collection.find()
# for i in data:
#     print(i)

print(json)