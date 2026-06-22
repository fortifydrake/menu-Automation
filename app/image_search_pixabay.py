import requests
import os
from dotenv import load_dotenv

load_dotenv()

PIXABAY_API_KEY = os.getenv("pixabay")


def search_pixabay_images(food_name, limit=6):

    query = f"{food_name} restaurant PLATED food"
    url = "https://pixabay.com/api/"

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "per_page": limit
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()
        
        images = []

        for img in data.get("hits", []):

            images.append({
                "food_item": food_name,
                "provider": "pixabay",
                "thumbnail": img["webformatURL"],
                "image_url": img["largeImageURL"],
                "source": img["pageURL"]
            })

        return images

    except Exception as e:

        print(
            f"Pixabay Error: {e}"
        )

        print(
            response.text[:500]
            if "response" in locals()
            else ""
        )

        return []

    