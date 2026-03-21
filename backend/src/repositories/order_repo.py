import os
import json
from src.schemas.order_schema import Order, OrderUpdate

class OrderRepo():

    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/order.json")

    @staticmethod
    async def get_all_orders():

        with open(OrderRepo.DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    async def get_order(order_id: str) -> Order:

        orders = await OrderRepo.get_all_orders()
        if order_id not in orders:
            raise ValueError("Order not found")
        return Order(**orders[order_id])

    @staticmethod
    async def update_order(order_id: str, update: OrderUpdate) -> Order:

        orders = await OrderRepo.get_all_orders()
        if order_id not in orders:
            raise ValueError("Order not found")
        order_data = orders[order_id]
        update_data = update.model_dump(exclude_unset= True)
        for key, value in update_data.items():
            order_data[key] = value
        orders[order_id] = order_data
        with open(OrderRepo.DATA_PATH, "w", encoding="utf=8") as f:
            json.dump(orders, f, indent=4)
        return Order(**order_data)

    @staticmethod
    async def get_orders_by_driver(driver: str):
        orders = await OrderRepo.get_all_orders()
        driver_orders = []
        for order_data in orders.values():
            if order_data.get("driver") == driver:
                driver_orders.append(Order(**order_data))
        return driver_orders
