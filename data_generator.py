import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')  # Indian names; use Faker() for global

categories = ["Sportswear", "Beauty", "Electronics", "Home Decor", "Books", "Fashion"]
products = {
    "Sportswear": ["Running Shoes", "Yoga Mat", "Gym Bag", "Track Pants"],
    "Beauty": ["Skincare Set", "Lipstick Kit", "Perfume", "Face Serum"],
    "Electronics": ["Wireless Earbuds", "Smart Watch", "Power Bank", "Bluetooth Speaker"],
    "Home Decor": ["Table Lamp", "Wall Art", "Cushion Set", "Vase"],
    "Books": ["Fiction Novel", "Self-Help Book", "Cookbook", "Biography"],
    "Fashion": ["Denim Jacket", "Sneakers", "Handbag", "Sunglasses"],
}
cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata"]

def generate_customers(n=80):
    rows = []
    for i in range(1, n + 1):
        cat = random.choice(categories)
        rows.append({
            "id": i,
            "name": fake.first_name(),
            "age": random.randint(18, 60),
            "city": random.choice(cities),
            "fav_category": cat,
            "last_purchase": random.choice(products[cat]),
            "total_spent": random.randint(500, 50000),
            "visits_per_month": random.randint(1, 25),
            "cart_abandoned": random.choice(["Yes", "No"]),
            "avg_order_value": random.randint(300, 8000),
            "active_time": random.choice(["Morning", "Afternoon", "Evening", "Night"]),
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate_customers(80)
    df.to_csv("customers.csv", index=False)
    print("✅ Generated customers.csv with", len(df), "customers")