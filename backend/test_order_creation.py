import asyncio
import json
import sys

sys.path.insert(0, ".")

from src.services.order_services import OrderService
from src.schemas.order_schema import OrderCreate


async def test_create_order():
    users = json.load(open("src/data/users.json"))
    restaurants = json.load(open("src/data/restaurants.json"))

    customer = [u for u in users if u.get("role") == "customer"][0]
    customer_username = customer["username"]

    first_rest_id = list(restaurants.keys())[0]
    restaurant_name = f"Restaurant_{first_rest_id}"

    print(f"\n{'=' * 60}")
    print(f"TESTING ORDER CREATION")
    print(f"{'=' * 60}")
    print(f"Customer: {customer_username}")
    print(f"Restaurant: {restaurant_name}")

    order_create = OrderCreate(
        items=[{"name": "Pizza", "price": 15.99}],
        restaurant=restaurant_name,
        customer=customer_username,
        time=0,
        cuisine="Italian",
        distance=None,
    )

    print(f"\n[TEST] Creating order with distance=None...")
    print(f"{'=' * 60}\n")

    try:
        created_order = await OrderService.create_order(order_create)
        print(f"\n{'=' * 60}")
        print(f"ORDER CREATED SUCCESSFULLY")
        print(f"{'=' * 60}")
        print(f"Order ID: {created_order.id}")
        print(f"Cost: ${created_order.cost}")

        all_orders = json.load(open("src/data/orders.json"))
        saved_order = all_orders.get(str(created_order.id))
        print(f"\nDistance in saved order: {saved_order.get('distance')} km")

        from src.utils.distance import calculate_distance

        customer_lon, customer_lat = customer["location"][0]
        restaurant = restaurants[first_rest_id]
        restaurant_lon, restaurant_lat = restaurant["location"]
        calc_distance = calculate_distance(
            customer_lon, customer_lat, restaurant_lon, restaurant_lat
        )
        expected_delivery_fee = 2.0 + (calc_distance * 0.5)
        expected_cost = (15.99 + expected_delivery_fee) * 1.13

        print(f"\n--- Expected Values ---")
        print(f"Expected distance: {calc_distance} km")
        print(f"Expected delivery fee: ${expected_delivery_fee:.2f}")
        print(f"Expected cost: ${expected_cost:.2f}")

        print(f"\n--- Comparison ---")
        if saved_order.get("distance") == 0.0:
            print(f"⚠️  WARNING: Distance is 0 (fixed fee only)")
        elif saved_order.get("distance") == calc_distance:
            print(f"✓ Distance properly calculated!")

    except Exception as e:
        print(f"\n❌ ERROR creating order: {e}")
        import traceback

        traceback.print_exc()


asyncio.run(test_create_order())
