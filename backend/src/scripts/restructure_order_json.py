import json

with open("backend/src/data/raw/deliveries.json", encoding="utf-8") as f:
    raw = json.load(f)

fixed_orders = {}

for order in raw:

    fixed_orders[order["order_id"]] = {
        "items": [order["food_item"]],
        "cost": order["order_value"],
        "restaurant": f"Restaurant_{order['restaurant_id']}",
        "customer": order["customer_id"],
        "time": order["delivery_time_actual"],
        "cuisine" : order["preferred_cuisine"],
        "distance": order["delivery_distance"]
    }

with open("backend/src/data/orders.json", "w", encoding="utf-8") as f:
    json.dump(fixed_orders, f, indent=4)
