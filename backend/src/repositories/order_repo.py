import os
import json
from src.schemas.order_schema import Order
import aiofiles

class OrderRepo():
    DATA_PATH = os.path.join(os.path.dirname(__file__), "backend/src/data/order.json")

    @staticmethod
    async def get_all_orders():
        
        with open(OrderRepo.DATA_PATH, "r") as f:
            return json.load(f)

    @staticmethod
    async def get_order(order_id: str) -> Order:

        orders = await Order.get_all_orders()
        if order_id not in orders:
            raise ValueError("Order not found")
        return Order(**orders[order_id])      
    
    async def update_order():
        pass

    async def get_orders_by_driver():
        pass

    # Work on this shit last
