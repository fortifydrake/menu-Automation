from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URl = os.getenv("MONGO_URl")
client = MongoClient(MONGO_URl)

db = client["menu_automation"]

foods = db["foods"]

def food_upload(final_records):

    for record in final_records:

        foods.update_one(
            {
                "food_name":
                record["food_name"]
            },
            {
                "$set": record
            },
            upsert=True
        )