# generate_products.py
"""
Generates 100 sample fast-food products and writes them to products.json.
Each product follows the structure required by the assignment.
"""
import json
import random
from datetime import datetime

random.seed(42)

CATEGORIES = [
    "Burgers", "Pizza", "Fried Chicken", "Tacos & Wraps", "Sides & Appetizers",
    "Beverages", "Desserts", "Salads", "Breakfast", "Limited Time Specials"
]

MOOD_TAGS = ["adventurous", "comfort", "indulgent", "healthy", "quick", "party"]
DIETARY = ["vegetarian", "vegan", "contains_gluten", "contains_dairy", "contains_soy", "gluten_free"]
INGREDIENT_POOL = ["beef patty", "chicken", "pork", "tofu", "kimchi", "gochujang", "brioche bun",
                   "jalapeño", "lime crema", "cheddar", "mozzarella", "bacon", "lettuce", "tomato"]

def make_product(i):
    pid = f"FF{i:03d}"
    category = random.choice(CATEGORIES)
    spice = random.randint(0, 10)
    price = round(random.uniform(3.99, 19.99), 2)
    calories = random.randint(150, 950)
    dietary = []
    if random.random() < 0.2:
        dietary.append("vegetarian")
    if random.random() < 0.1:
        dietary.append("vegan")
    if random.random() < 0.5:
        dietary.append("contains_gluten")
    if random.random() < 0.4:
        dietary.append("contains_dairy")
    mood = random.sample(MOOD_TAGS, k=random.randint(1,2))
    allergens = []
    if "contains_gluten" in dietary:
        allergens.append("gluten")
    if "contains_dairy" in dietary:
        allergens.append("dairy")
    ingredients = random.sample(INGREDIENT_POOL, k= random.randint(3,6))
    name = f"{random.choice(['Fire','Spicy','Classic','Crispy','Fusion','Smoky','Zesty'])} {random.choice(['Dragon','Ranch','BBQ','Cheese','Garden','Deluxe'])} {random.choice(['Burger','Tacos','Pizza','Wrap','Sandwich','Bowl'])}"
    description = f"{name}: {' '.join(random.sample(['Bold flavors','handcrafted','crispy','tender','smoky','with a kick','chef-special','perfect for sharing'], 3))}."
    image_url = f"https://picsum.photos/seed/{pid}/400/300"  # placeholder images
    return {
        "product_id": pid,
        "name": name,
        "category": category,
        "description": description,
        "ingredients": ingredients,
        "price": price,
        "calories": calories,
        "prep_time": f"{random.randint(5,20)} mins",
        "dietary_tags": dietary,
        "mood_tags": mood,
        "allergens": allergens,
        "popularity_score": random.randint(10, 100),
        "chef_special": random.random() < 0.12,
        "limited_time": random.random() < 0.08,
        "spice_level": spice,
        "image_prompt": f"{name} {', '.join(ingredients)}",
        "image_url": image_url
    }

def main():
    products = [make_product(i) for i in range(1, 101)]
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)
    print("Wrote products.json with 100 items.")

if __name__ == "__main__":
    main()
