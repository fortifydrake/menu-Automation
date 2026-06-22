import os
from dotenv import load_dotenv
import requests
load_dotenv()
headers ={
    "Authorization" : os.getenv("pexel")
}

def search_image_pexel(food):
    
    
    query = f"gourmet {food} plated meal, professional food photography, bright studio lighting, minimalist composition, top-down view"
    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params={
            "query": query,
            "per_page": 6
        }
    )
    
    normalized = []

    for img in response.json()["photos"]:

        normalized.append({
            "food_item": food,
            "provider": "pexels",
            "title": food,
            "thumbnail": img["src"]["medium"],
            "image_url": img["src"]["original"],
            "source": img["url"]
        })

    return normalized
