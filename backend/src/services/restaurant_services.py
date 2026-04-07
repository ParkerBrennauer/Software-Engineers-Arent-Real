from src.services.item_services import ItemService
from src.repositories.restaurant_repo import RestaurantRepo
from src.schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate

class RestaurantService:
    @staticmethod
    async def get_all_restaurants() -> list:
        restaurants = await RestaurantRepo.read_all()
        return list(restaurants.values())

    @staticmethod
    async def get_restaurants_search(query: str) -> list:
        restaurants = await RestaurantRepo.read_all()
        results = []

        for restaurant in restaurants.values():
            if query in str(restaurant["restaurant_id"]):
                results.append(restaurant)
        return results

    @staticmethod
    async def get_restaurants_search_advance(query: str, filters: list, sort: str) -> list:
        restaurants = await RestaurantRepo.read_all()
        query = query.casefold()
        results = []

        for restaurant in restaurants.values():
            # will update with more filters once added
            attributes = [restaurant["cuisine"]]
            matches_filter = False

            # will change to name once added
            if query in str(restaurant["restaurant_id"]):
                for search_filter in filters:
                    if search_filter in attributes:  # will update
                        matches_filter = True
                        break
                if matches_filter:
                    results.append(restaurant)

        if sort == "AlphabetAsc":
            # will change to name once added
            results.sort(key=lambda r: r.get("restaurant_id"),)
        elif sort == "AlphabetDesc":
            results.sort(key=lambda r: r.get("restaurant_id"),
                         reverse=True)  # will change to name once added
        elif sort == "RatingAsc":
            results.sort(key=lambda r: float(r.get("avg_ratings", 0)))
        elif sort == "RatingDesc":
            results.sort(key=lambda r: float(r.get("avg_ratings", 0)),
                         reverse=True)
        return results

    @staticmethod
    async def get_restaurant_menu(restaurant_id: int) -> list:
        restaurants = await RestaurantRepo.read_all()

        if str(restaurant_id) not in restaurants:
            raise ValueError("Restaurant not found")

        menu = await ItemService.get_items_by_restaurant_id(restaurant_id)
        return menu

    @staticmethod
    async def create_restaurant(restaurant_in: RestaurantCreate) -> dict:
        restaurant_data = restaurant_in.model_dump()

        restaurant_data["menu"] = [item.model_dump()
                                   for item in restaurant_in.menu]

        saved = await RestaurantRepo.save_restaurant(restaurant_data)
        return saved

    @staticmethod
    async def update_restaurant(restaurant_id: int, restaurant_in: RestaurantUpdate) -> dict:
        update_data = restaurant_in.model_dump(
            exclude_unset=True, exclude_none=True)

        if not update_data:
            existing = await RestaurantRepo.get_restaurant_by_id(restaurant_id)
            if existing:
                return existing
            raise ValueError("Restaurant not found")

        if "menu" in update_data:
            update_data["menu"] = [item.model_dump()
                                   for item in restaurant_in.menu]

        updated = await RestaurantRepo.update_by_restaurant_id(restaurant_id, update_data)
        if not updated:
            raise ValueError("Restaurant not found")

        return updated

