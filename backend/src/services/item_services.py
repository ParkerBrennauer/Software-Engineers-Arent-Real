from src.repositories.item_repo import ItemRepo
from src.schemas.item_schema import ItemUpdate, ItemUpdateAnalytics, ItemCreate


class ItemService:
    @staticmethod
    async def get_items_by_key(key: str) -> list:
        items = await ItemRepo.get_by_key(key)
        return items

    @staticmethod
    async def get_items_by_restaurant_id(restaurant_id: int) -> list:
        items = await ItemRepo.get_by_restaurant_id(restaurant_id)
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

    @staticmethod
    async def create_item(item_in: ItemCreate) -> dict:
        item_data = item_in.model_dump(exclude_none=True)

        # ensure dietary is JSON-friendly if it's a Pydantic model
        if "dietary" in item_data and item_data["dietary"] is not None:
            dietary_obj = item_in.dietary
            if hasattr(dietary_obj, "model_dump"):
                item_data["dietary"] = dietary_obj.model_dump()

        item_key = f"{item_data['item_name']}_{item_data['restaurant_id']}"

        existing = await ItemRepo.get_by_key(item_key)
        if existing:
            raise ValueError("Item already exists")

        saved = await ItemRepo.save_item(item_data)
        return saved

