# backend/scripts/create_indexes.py
from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
coll = client["fxdb"]["exchange_rates"]
coll.create_index([("date", ASCENDING), ("pair", ASCENDING)], unique=True)
print("index created")
