from database import food_collection

def normalize_food_name(name):
    return (
        name.lower()
            .strip()
            .replace("-", " ")
    )
    
    
def get_food(food_name):

    normalized_name = normalize_food_name(
        food_name
    )

    food = food_collection.find_one(
        {
            "normalized_name":
            normalized_name
        }
    )

    return food