from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
db_url = os.getenv('db')

MONGO_URI = db_url

client = MongoClient(MONGO_URI)

db = client["menu_automation"]

food_collection = db["foods"]