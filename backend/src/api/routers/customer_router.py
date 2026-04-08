from fastapi import APIRouter, status
from src.api.dependencies import convert_service_error
from src.schemas.favorite_restaurant_schema import (
    FavoriteRestaurantMutationResponse,
    FavoriteRestaurantResponse,
)
from src.services.favorite_restaurant_service import FavoriteRestaurantService
from src.services.customer_service import CustomerService
from src.services.user_service import UserService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get(
    "/favorites/restaurants",
    response_model=FavoriteRestaurantResponse,
    status_code=status.HTTP_200_OK,
)
async def get_favorite_restaurants():
    customer_id = UserService.get_current_user()
    if not customer_id:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        return await FavoriteRestaurantService.get_favorite_restaurants(customer_id)
    except ValueError as err:
        raise convert_service_error(err) from err


@router.post(
    "/favorites/restaurants/{restaurant_id}",
    response_model=FavoriteRestaurantMutationResponse,
    status_code=status.HTTP_200_OK,
)
async def add_favorite_restaurant(restaurant_id: int):
    customer_id = UserService.get_current_user()
    if not customer_id:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        return await FavoriteRestaurantService.add_favorite_restaurant(
            customer_id, restaurant_id
        )
    except ValueError as err:
        raise convert_service_error(err) from err


@router.delete(
    "/favorites/restaurants/{restaurant_id}",
    response_model=FavoriteRestaurantMutationResponse,
    status_code=status.HTTP_200_OK,
)
async def remove_favorite_restaurant(restaurant_id: int):
    customer_id = UserService.get_current_user()
    if not customer_id:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        return await FavoriteRestaurantService.remove_favorite_restaurant(
            customer_id, restaurant_id
        )
    except ValueError as err:
        raise convert_service_error(err) from err


@router.patch("/order-history")
async def order_history():
    customer_id = UserService.get_current_user()
    if not customer_id:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        return await CustomerService.get_order_history(customer_id)
    except ValueError as err:
        raise convert_service_error(err) from err


@router.patch("/favourites/{item_key}")
async def toggle_favourite_item(item_key):
    customer_id = UserService.get_current_user()
    if not customer_id:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        return await CustomerService.toggle_favourite(customer_id, item_key)
    except ValueError as err:
        raise convert_service_error(err) from err


@router.get("/favourites")
async def get_favourite_items():
    customer_id = UserService.get_current_user()
    if not customer_id:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        return await CustomerService.get_favourites(customer_id)
    except ValueError as err:
        raise convert_service_error(err) from err
