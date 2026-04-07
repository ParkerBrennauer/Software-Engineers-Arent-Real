from fastapi import APIRouter, status

from src.api.dependencies import convert_service_error
from src.schemas.favorite_restaurant_schema import (
    FavoriteRestaurantMutationResponse,
    FavoriteRestaurantResponse,
)
from src.services.favorite_restaurant_service import FavoriteRestaurantService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get(
    "/{customer_id}/favorites/restaurants",
    response_model=FavoriteRestaurantResponse,
    status_code=status.HTTP_200_OK,
)
async def get_favorite_restaurants(customer_id: str):
    try:
        return await FavoriteRestaurantService.get_favorite_restaurants(customer_id)
    except ValueError as err:
        raise convert_service_error(err) from err


@router.post(
    "/{customer_id}/favorites/restaurants/{restaurant_id}",
    response_model=FavoriteRestaurantMutationResponse,
    status_code=status.HTTP_200_OK,
)
async def add_favorite_restaurant(customer_id: str, restaurant_id: int):
    try:
        return await FavoriteRestaurantService.add_favorite_restaurant(
            customer_id,
            restaurant_id,
        )
    except ValueError as err:
        raise convert_service_error(err) from err


@router.delete(
    "/{customer_id}/favorites/restaurants/{restaurant_id}",
    response_model=FavoriteRestaurantMutationResponse,
    status_code=status.HTTP_200_OK,
)
async def remove_favorite_restaurant(customer_id: str, restaurant_id: int):
    try:
        return await FavoriteRestaurantService.remove_favorite_restaurant(
            customer_id,
            restaurant_id,
        )
    except ValueError as err:
        raise convert_service_error(err) from err
