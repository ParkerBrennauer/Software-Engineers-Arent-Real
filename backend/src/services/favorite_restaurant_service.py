from src.repositories.restaurant_repo import RestaurantRepo
from src.repositories.user_repo import UserRepo
from src.schemas.favorite_restaurant_schema import FavoriteRestaurantMutationResponse, FavoriteRestaurantResponse

class FavoriteRestaurantService:

    @staticmethod
    def _coerce_favorites(user: dict) -> list[int]:
        favorites: list[int] = []
        for restaurant_id in user.get('favorite_restaurants', []):
            favorites.append(int(restaurant_id))
        return favorites

    @staticmethod
    async def _get_customer(username: str) -> dict:
        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError('User not found')
        return user

    @staticmethod
    async def _restaurant_exists(restaurant_id: int) -> bool:
        restaurants = await RestaurantRepo.read_all()
        restaurant_records = restaurants.values() if isinstance(restaurants, dict) else restaurants
        for restaurant in restaurant_records:
            if int(restaurant.get('restaurant_id', restaurant.get('id', -1))) == restaurant_id:
                return True
        return False

    @staticmethod
    async def get_favorite_restaurants(username: str) -> FavoriteRestaurantResponse:
        user = await FavoriteRestaurantService._get_customer(username)
        favorites = FavoriteRestaurantService._coerce_favorites(user)
        return FavoriteRestaurantResponse(customer_id=username, favorite_restaurants=favorites)

    @staticmethod
    async def add_favorite_restaurant(username: str, restaurant_id: int) -> FavoriteRestaurantMutationResponse:
        user = await FavoriteRestaurantService._get_customer(username)
        if not await FavoriteRestaurantService._restaurant_exists(restaurant_id):
            raise ValueError('Restaurant not found')
        favorites = FavoriteRestaurantService._coerce_favorites(user)
        if restaurant_id in favorites:
            raise ValueError('Restaurant is already in favorites')
        updated_favorites = [*favorites, restaurant_id]
        updated_user = await UserRepo.update_by_username(username, {'favorite_restaurants': updated_favorites})
        if not updated_user:
            raise ValueError('User not found')
        return FavoriteRestaurantMutationResponse(customer_id=username, restaurant_id=restaurant_id, favorite_restaurants=FavoriteRestaurantService._coerce_favorites(updated_user), message='Restaurant added to favorites')

    @staticmethod
    async def remove_favorite_restaurant(username: str, restaurant_id: int) -> FavoriteRestaurantMutationResponse:
        user = await FavoriteRestaurantService._get_customer(username)
        favorites = FavoriteRestaurantService._coerce_favorites(user)
        if restaurant_id not in favorites:
            raise ValueError('Restaurant is not in favorites')
        updated_favorites = [favorite_id for favorite_id in favorites if favorite_id != restaurant_id]
        updated_user = await UserRepo.update_by_username(username, {'favorite_restaurants': updated_favorites})
        if not updated_user:
            raise ValueError('User not found')
        return FavoriteRestaurantMutationResponse(customer_id=username, restaurant_id=restaurant_id, favorite_restaurants=FavoriteRestaurantService._coerce_favorites(updated_user), message='Restaurant removed from favorites')
