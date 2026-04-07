from pydantic import BaseModel


class FavoriteRestaurantResponse(BaseModel):
    customer_id: str
    favorite_restaurants: list[int]


class FavoriteRestaurantMutationResponse(FavoriteRestaurantResponse):
    restaurant_id: int
    message: str
