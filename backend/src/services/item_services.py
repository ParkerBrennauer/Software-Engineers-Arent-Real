from backend.src.repositories.item_repo import ItemRepo
from backend.src.schemas.item_schema import ItemUpdate, ItemUpdateAnalytics


class ItemService:
    @staticmethod
    async def get_items_by_key(key: str) -> list:
        items = await ItemRepo.get_by_key(key)
        return items

    @staticmethod
    async def get_items_by_restaurant_id(id: int) -> list:
        items = await ItemRepo.get_by_restaurant_id(id)
        return items

    @staticmethod
    async def update_item_by_key(item_key: str, item_in: ItemUpdate) -> dict:

        update_data = item_in.model_dump(exclude_unset=True, exclude_none=True)

        result = await ItemRepo.update_by_key(item_key, update_data)
        if not result:
            raise ValueError("Item does not exist")

        return result

    @staticmethod
    async def analytics_update_item_by_key(item_key: str, item_in: ItemUpdateAnalytics) -> dict:

        update_data = item_in.model_dump(exclude_unset=True, exclude_none=True)

        result = await ItemRepo.update_by_key(item_key, update_data)
        if not result:
            raise ValueError("Item does not exist")

        return result
