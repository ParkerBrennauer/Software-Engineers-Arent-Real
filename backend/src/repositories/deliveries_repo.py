import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"
RESTAURANTS_PATH = Path(__file__).resolve().parents[1] / "data" / "restaurants.json"


def load_orders():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_orders(orders):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)


def load_restaurants():
    with open(RESTAURANTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_order(order_id: str):
    orders = load_orders()
    return orders.get(order_id)


def get_restaurant_by_order(order_id: str):
    """Find which restaurant an order belongs to."""
    restaurants = load_restaurants()
    for rest_id, rest_data in restaurants.items():
        if order_id in rest_data.get("order_ids", []):
            return int(rest_id)
    return None


def update_rating(order_id: str, stars: int):
    orders = load_orders()

    if order_id not in orders:
        return None

    orders[order_id]["submitted_stars"] = stars

    save_orders(orders)

    return orders[order_id]


def update_review(order_id: str, review_text: str):
    orders = load_orders()

    if order_id not in orders:
        return None

    orders[order_id]["review_text"] = review_text

    save_orders(orders)

    return orders[order_id]


def edit_review(order_id: str, stars: int = None, review_text: str = None):
    orders = load_orders()

    if order_id not in orders:
        return None

    if stars is not None:
        orders[order_id]["submitted_stars"] = stars
    if review_text is not None:
        orders[order_id]["review_text"] = review_text

    save_orders(orders)

    return orders[order_id]


def delete_review(order_id: str):
    orders = load_orders()

    if order_id not in orders:
        return None

    orders[order_id]["submitted_stars"] = None
    orders[order_id]["review_text"] = None

    save_orders(orders)

    return orders[order_id]
