from src.repositories.customer_repo import CustomerRepo
from src.repositories.restaurant_repo import RestaurantRepo
from src.schemas.favorite_restaurant_schema import FavoriteRestaurantMutationResponse, FavoriteRestaurantResponse

class FavoriteRestaurantService:

    @staticmethod
    def _coerce_favorites(customer: dict) -> list[int]:
        favorites: list[int] = []
        for restaurant_id in customer.get('favorite_restaurants', []):
            favorites.append(int(restaurant_id))
        return favorites

    @staticmethod
    async def _get_customer(customer_id: str) -> dict:
        customer = await CustomerRepo.get_by_id(customer_id)
        if not customer:
            raise ValueError('Customer not found')
        return customer

    @staticmethod
    async def _restaurant_exists(restaurant_id: int) -> bool:
        restaurants = await RestaurantRepo.read_all()
        restaurant_records = restaurants.values() if isinstance(restaurants, dict) else restaurants
        for restaurant in restaurant_records:
            if int(restaurant.get('restaurant_id', restaurant.get('id', -1))) == restaurant_id:
                return True
        return False

    @staticmethod
    async def get_favorite_restaurants(customer_id: str) -> FavoriteRestaurantResponse:
        customer = await FavoriteRestaurantService._get_customer(customer_id)
        favorites = FavoriteRestaurantService._coerce_favorites(customer)
        return FavoriteRestaurantResponse(customer_id=customer_id, favorite_restaurants=favorites)

    @staticmethod
    async def add_favorite_restaurant(customer_id: str, restaurant_id: int) -> FavoriteRestaurantMutationResponse:
        customer = await FavoriteRestaurantService._get_customer(customer_id)
        if not await FavoriteRestaurantService._restaurant_exists(restaurant_id):
            raise ValueError('Restaurant not found')
        favorites = FavoriteRestaurantService._coerce_favorites(customer)
        if restaurant_id in favorites:
            raise ValueError('Restaurant is already in favorites')
        updated_favorites = [*favorites, restaurant_id]
        updated_customer = await CustomerRepo.update_by_id(customer_id, {'favorite_restaurants': updated_favorites})
        if not updated_customer:
            raise ValueError('Customer not found')
        return FavoriteRestaurantMutationResponse(customer_id=customer_id, restaurant_id=restaurant_id, favorite_restaurants=FavoriteRestaurantService._coerce_favorites(updated_customer), message='Restaurant added to favorites')

    @staticmethod
    async def remove_favorite_restaurant(customer_id: str, restaurant_id: int) -> FavoriteRestaurantMutationResponse:
        customer = await FavoriteRestaurantService._get_customer(customer_id)
        favorites = FavoriteRestaurantService._coerce_favorites(customer)
        if restaurant_id not in favorites:
            raise ValueError('Restaurant is not in favorites')
        updated_favorites = [favorite_id for favorite_id in favorites if favorite_id != restaurant_id]
        updated_customer = await CustomerRepo.update_by_id(customer_id, {'favorite_restaurants': updated_favorites})
        if not updated_customer:
            raise ValueError('Customer not found')
        return FavoriteRestaurantMutationResponse(customer_id=customer_id, restaurant_id=restaurant_id, favorite_restaurants=FavoriteRestaurantService._coerce_favorites(updated_customer), message='Restaurant removed from favorites')
