from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from src.schemas.restaurant_schema import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantSearchAdvanced,
)
from src.services.restaurant_services import RestaurantService
from src.services.user_services import UserService
from src.services.order_services import OrderService
from src.api.dependencies import convert_service_error

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_restaurants():
    restaurants = await RestaurantService.get_all_restaurants()
    return restaurants


@router.get("/search/{query}", status_code=status.HTTP_200_OK)
async def search_restaurants(query: str):
    results = await RestaurantService.get_restaurants_search(query)
    return results


@router.post(
    "/search/advanced/{query}/{filters}/{sort}", status_code=status.HTTP_200_OK
)
async def search_restaurants_advanced(body: RestaurantSearchAdvanced):
    results = await RestaurantService.get_restaurants_search_advance(
        body.query, body.filters, body.sort
    )
    return results


@router.get("/{restaurant_id}/delivery-info", status_code=status.HTTP_200_OK)
async def get_delivery_info(restaurant_id: int):
    try:
        current_user = UserService.get_current_user()
        if not current_user:
            raise ValueError("User not logged in")
        distance = await OrderService.get_distance(
            current_user, f"Restaurant_{restaurant_id}"
        )
        delivery_fee = 2.0 + distance * 0.5
        return {"distance": distance, "delivery_fee": round(delivery_fee, 2)}
    except ValueError as err:
        raise convert_service_error(err)


@router.get("/{restaurant_id}/menu", status_code=status.HTTP_200_OK)
async def get_restaurant_menu(restaurant_id: int):
    try:
        menu = await RestaurantService.get_restaurant_menu(restaurant_id)
        return menu
    except ValueError as err:
        raise convert_service_error(err)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_restaurant(restaurant_in: RestaurantCreate):
    try:
        created = await RestaurantService.create_restaurant(restaurant_in)
        return created
    except ValueError as err:
        raise convert_service_error(err)


@router.patch("/{restaurant_id}", status_code=status.HTTP_200_OK)
async def update_restaurant(restaurant_id: int, restaurant_in: RestaurantUpdate):
    try:
        updated = await RestaurantService.update_restaurant(
            restaurant_id, restaurant_in
        )
        return updated
    except ValueError as err:
        message = str(err)
        if message == "Restaurant not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err
