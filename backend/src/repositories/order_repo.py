import json
from typing import List, Optional
import aiofiles
import os

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
    async def get_by_id(cls, order_id: int) -> dict:
        orders = await cls.read_all()

        for order in orders:
            if order["id"] == order_id:
                return order
        return None

    @classmethod
    async def save_order(cls, order_data: dict) -> dict:
        order = await cls.read_all()

        new_id = max((u.get("id", 0) for u in order), default=0) + 1
        order_data["id"] = new_id
        order.append(order_data)

        async with aiofiles.open(cls.FilePath, mode='w') as f:
            await f.write(json.dumps(order, indent=4))

        return order_data

    @classmethod
    async def update_by_id(cls, order_id: int, updates: dict, completed: bool) -> Optional[dict]:
        if(completed):
             return None

        orders = await cls.read_all()

        for index, order in enumerate(orders):
            if order["id"] == order_id:
                orders[index].update(updates)

                async with aiofiles.open(cls.FilePath, mode='w') as f:
                    await f.write(json.dumps(orders, indent=4))

                return orders[index]

        return None
