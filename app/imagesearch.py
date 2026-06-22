from image_searchDB import get_food
from image_search_pixabay import search_pixabay_images
from image_search_pexel import search_image_pexel

def image_search(df):
    results = []
    
    for _, row in df.iterrows():

        food_name = row["food_item"]

        food = get_food(food_name)

        if food:

            results.append({
                "food_item": food_name,
                "found": True,
                "image_url": food["image_url"],
                "image_source": "mongodb",
                "candidate_images": []
            })

        else:

            pixabay = search_pixabay_images(food_name)

            pexels = search_image_pexel(food_name)

            results.append({
                "food_item": food_name,
                "found": False,
                "image_url": None,
                "image_source": None,
                "candidate_images": pixabay + pexels
            })  
            
    return results