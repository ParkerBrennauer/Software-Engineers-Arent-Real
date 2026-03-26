import json
from typing import List, Optional
import aiofiles

from src.core.config import RESTAURANTS_FILE


class RestaurantRepo:
    FILE_PATH = RESTAURANTS_FILE

    @classmethod
    async def read_all(cls) -> List[dict]:

        if not cls.FILE_PATH.exists():
            return []

        async with aiofiles.open(cls.FILE_PATH, mode="r") as f:
            restaurants = await f.read()
            return json.loads(restaurants) if restaurants else []

    @classmethod
    async def write_restaurant(cls, data: dict) -> None:
        async with aiofiles.open(cls.FILE_PATH, mode="w") as f:
            await f.write(json.dumps(data, indent=1))

    @classmethod
    async def save_restaurant(cls, restaurant_data: dict) -> dict:
        restaurants = await cls.read_all()

        if restaurant_data.get("restaurant_id") is not None:
            new_id = restaurant_data["restaurant_id"]
        else:
            new_id = max((r.get("id", 0) for r in restaurants), default=0) + 1

        restaurant_data["id"] = new_id
        restaurants.append(restaurant_data)

        await cls.write_restaurant(restaurants)

        return restaurant_data

    @classmethod
    async def get_restaurant_by_id(cls) -> dict:
        if not cls.FILE_PATH.exists():
            return {}

        async with aiofiles.open(cls.FILE_PATH, mode="r") as f:
            items = await f.read()
            if not items:
                return {}

            return json.loads(items) if items else {}

    @classmethod
    async def update_by_restaurant_id(
        cls, restaurant_id: int, updates: dict
    ) -> Optional[dict]:
        restaurants = await cls.read_all()

        for index, r in enumerate(restaurants):
            if r.get("restaurant_id") == restaurant_id:
                restaurants[index].update(updates)

                await cls.write_restaurant(restaurants)

                return restaurants[index]

        return None
