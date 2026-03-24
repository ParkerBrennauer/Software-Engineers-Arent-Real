import json
from typing import List, Optional
import os
import aiofiles


class OrderRepo:
    FilePath = "orders.json"

    @classmethod
    async def read_all(cls) -> List[dict]:
        if not os.path.exists(cls.FilePath):
            return []

        async with aiofiles.open(cls.FilePath, mode='r') as f:
            orders = await f.read()
            return json.loads(orders) if orders else []

    @classmethod
    async def get_by_id(cls, order_id: int) -> Optional[dict]:
        orders = await cls.read_all()

        for order in orders:
            if order["id"] == order_id:
                return order
        return None

    @classmethod
    async def save_order(cls, order_data: dict) -> dict:
        orders = await cls.read_all()

        new_id = max((o.get("id", 0) for o in orders), default=0) + 1
        order_data["id"] = new_id
        orders.append(order_data)

        async with aiofiles.open(cls.FilePath, mode='w') as f:
            await f.write(json.dumps(orders, indent=4))

        return order_data

    @classmethod
    async def update_order(cls, order_id: int, updated_data: dict) -> Optional[dict]:
        orders = await cls.read_all()

        for index, order in enumerate(orders):
            if order["id"] == order_id:
                orders[index] = updated_data

                async with aiofiles.open(cls.FilePath, mode='w') as f:
                    await f.write(json.dumps(orders, indent=4))

                return orders[index]

        return None

    @classmethod
    async def get_largest_order_id(cls) -> int:
        orders = await cls.read_all()
        return max((order.get("id", 0) for order in orders), default=0)

    @classmethod
    async def get_orders_by_driver(cls, driver: str) -> List[dict]:
        orders = await cls.read_all()
        return [order for order in orders if order.get("driver") == driver]

    @classmethod
    async def get_order(cls, order_id: int):
        return await cls.get_by_id(order_id)

    @classmethod
    async def get_all_orders(cls):
        orders = await cls.read_all()

        return {str(order["id"]): order for order in orders}
