import json
from typing import List
import os
import aiofiles


class RestaurantRepo:
    FILE_PATH = "../data/restaurants.json"

    @classmethod
    async def read_all(cls) -> List[dict]:

        if not os.path.exists(cls.FILE_PATH):
            return []

        async with aiofiles.open(cls.FILE_PATH, mode='r') as f:
            restaurants = await f.read()
            return json.loads(restaurants) if restaurants else []

    @classmethod
    async def save_restaurant(cls, restaurant_data: dict) -> dict:
        restaurants = await cls.read_all()

        new_id = max((r.get("id", 0) for r in restaurants), default=0) + 1
        restaurant_data["id"] = new_id
        restaurants.append(restaurant_data)

        async with aiofiles.open(cls.FILE_PATH, mode='w') as f:
            await f.write(json.dumps(restaurants, indent=1))

        return restaurant_data
