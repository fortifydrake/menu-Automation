from db.mongo import foods

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

    food = foods.find_one(
        {
            "normalized_name":
            normalized_name
        }
    )

    return food