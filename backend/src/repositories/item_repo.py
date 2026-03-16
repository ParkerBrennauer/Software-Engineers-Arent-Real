import json
from typing import List, Optional
import os
import aiofiles


class ItemRepo:
    FILE_PATH = "backend/src/data/items.json"

    @classmethod
    async def read_all(cls) -> dict:

        if not os.path.exists(cls.FILE_PATH):
            return {}

        async with aiofiles.open(cls.FILE_PATH, mode='r') as f:
            items = await f.read()
            if not items:
                return {}

            return json.loads(items) if items else {}

    @classmethod
    async def write_all(cls, data: dict) -> None:
        async with aiofiles.open(cls.FILE_PATH, "w") as f:
            await f.write(json.dumps(data, indent=1))


    @classmethod
    async def save_item(cls, item_data: dict) -> dict:

        item_name = item_data["item_name"]
        restaurant_id = item_data["restaurant_id"]
        item_key = f"{item_name}_{restaurant_id}"

        data = await cls.read_all()

        if item_key not in data:
            data[item_key] = item_data
        else:
            data[item_key].update(item_data)

        await cls.write_all(data)

        return data[item_key]

    @classmethod
    async def update_by_key(cls, old_key: str, updates: dict) -> Optional[dict]:
        data = await cls.read_all()

        if old_key not in data:
            return None

        update_item = dict(data[old_key])
        update_item.update(updates)
        item_name = update_item.get("item_name")
        restaurant_id = update_item.get("restaurant_id")
        new_key = f"{item_name}_{restaurant_id}"

        if new_key != old_key and new_key in data:
            raise ValueError("Updated item key already exists")

        if new_key != old_key:
            del data[old_key]
        data[new_key] = update_item

        await cls.write_all(data)

        result = dict(update_item)
        result["key"] = new_key
        return result


    @classmethod
    async def get_by_key(cls, item_key: str) -> Optional[dict]:
        data = await cls.read_all()
        return data.get(item_key)

    @classmethod
    async def get_by_restaurant_id(cls, restaurant_id: int) -> List[dict]:
        data = await cls.read_all()

        results = []
        for key, value in data.items():
            if value.get("restaurant_id") == restaurant_id:
                results.append(value)

        return results

    @classmethod
    async def get_by_name(cls, item_key: str) -> Optional[dict]:
        data = await cls.read_all()
        return data.get(item_key)


