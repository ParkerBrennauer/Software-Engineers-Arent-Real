from src.repositories.item_repo import ItemRepo
from src.schemas.item_schema import ItemUpdate, ItemUpdateAnalytics


class ItemService:
    @staticmethod
    async def get_items_by_key(key: str) -> list:
        items = await ItemRepo.get_by_key(key)
        return items

    @staticmethod
    async def get_items_by_restaurant_id(restaurant_id: int) -> list:
        items = await ItemRepo.get_by_restaurant_id(restaurant_id)
        return items
