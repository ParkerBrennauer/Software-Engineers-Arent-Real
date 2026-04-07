import json
from typing import List, Optional
import aiofiles

from src.core.config import RESTAURANTS_FILE


class RestaurantRepo:
    FILE_PATH = RESTAURANTS_FILE

    @classmethod
    async def read_all(cls) -> dict:

        if not cls.FILE_PATH.exists():
            return []

        async with aiofiles.open(cls.FILE_PATH, mode="r") as f:
            restaurants = await f.read()
            return json.loads(restaurants) if restaurants else {}

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
            new_id = max((int(key) for key in restaurants.keys()), default=0) + 1

        restaurant_data["restaurant_id"] = new_id
        restaurants[str(new_id)] = restaurant_data

        await cls.write_restaurant(restaurants)
        return restaurant_data

    @classmethod
    async def get_restaurant_by_id(cls, restaurant_id: int) -> Optional[dict]:
        restaurants = await cls.read_all()
        key = str(restaurant_id)

        if key not in restaurants:
            return None

        return restaurants.get(key, {})

    @classmethod
    async def update_by_restaurant_id(cls, restaurant_id: int, updates: dict) -> Optional[dict]:
        restaurants = await cls.read_all()
        key = str(restaurant_id)

        if key not in restaurants:
            return None

        restaurants[key].update(updates)
        await cls.write_restaurant(restaurants)

        return restaurants[key]
