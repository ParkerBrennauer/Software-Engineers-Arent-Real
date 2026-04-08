from src.services.order_services import OrderService
from src.repositories.user_repo import UserRepo
from src.repositories.item_repo import ItemRepo

class CustomerService:
    @staticmethod
    async def get_order_history(username: str) -> list:
        if not username:
            raise ValueError("No username submitted")
        return await OrderService.get_previous_orders_by_user(username)

    @staticmethod
    async def get_favourites(username: str) -> list:
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username is empty")

        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError("User not found")

        return user.get("favourites", [])


    @staticmethod
    async def toggle_favourite(username: str, item_key: str) -> str:
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username is empty")
        if not isinstance(item_key, str) or not item_key.strip():
            raise ValueError("itemKey is empty")

        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError("User not found")

        item = await ItemRepo.get_by_key(item_key)
        if not item:
            raise ValueError("Item not found")

        restaurant_id = item.get("restaurant_id")
        if restaurant_id is None:
            raise ValueError("Item missing restaurant_id")

        favorites_list = user.get("favourites", [])
        if not isinstance(favorites_list, list):
            raise ValueError("User favourites must be a list")
        favourites = list(favorites_list)

        if item_key in favourites:
            updated = [fav for fav in favourites if fav != item_key]
            await UserRepo.update_by_username(username, {"favourites": updated})
            return "removed"

        replaced = False
        updated_favourites: list[str] = []
        for favourite_key in favourites:
            favourite_item = await ItemRepo.get_by_key(favourite_key)
            favourite_restaurant_id = (
                favourite_item.get("restaurant_id")
                if isinstance(favourite_item, dict)
                else None
            )
            if favourite_restaurant_id == restaurant_id:
                replaced = True
                continue
            updated_favourites.append(favourite_key)

        updated_favourites.append(item_key)
        await UserRepo.update_by_username(username, {"favourites": updated_favourites})
        return "replaced" if replaced else "added"
