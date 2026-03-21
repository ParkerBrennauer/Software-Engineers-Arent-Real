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