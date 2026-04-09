from fastapi import APIRouter, status
from src.schemas.user_schema import UserResponse
from src.schemas.order_schema import Order
from src.services.restaurant_owner_services import RestaurantOwnerService
from src.services.user_service import UserService
from src.schemas.restaurant_owner_schema import (
    RestaurantOwnerAssignStaffRequest as StaffAssignmentRequest,
)
from src.api.dependencies import convert_service_error

router = APIRouter(
    prefix="/restaurant_administration", tags=["users", "restaurant_administration"]
)


@router.post("/staff", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def assign_staff(body: StaffAssignmentRequest):
    owner_username = UserService.get_current_user()
    if not owner_username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        updated_user = await RestaurantOwnerService.assign_user_as_staff(
            owner_username, body.staff_username
        )
        return updated_user
    except ValueError as err:
        raise convert_service_error(err)


@router.patch(
    "/restaurants/{restaurant_id}/venue",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def switch_venue(restaurant_id: int):
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        updated_user = await RestaurantOwnerService.switch_venue(
            username, restaurant_id
        )
        return updated_user
    except ValueError as err:
        raise convert_service_error(err)


@router.get(
    "/restaurants/{restaurant_id}/orders",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
async def get_restaurant_orders(restaurant_id: int):
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders(
            restaurant_id, username
        )
        return orders
    except ValueError as err:
        raise convert_service_error(err)


@router.get(
    "/restaurants/{restaurant_id}/orders/filter/status",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
async def get_restaurant_orders_by_status(restaurant_id: int, order_status: str):
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders_by_status(
            restaurant_id, username, order_status
        )
        return orders
    except ValueError as err:
        raise convert_service_error(err)


@router.get(
    "/restaurants/{restaurant_id}/orders/filter/date",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
async def get_restaurant_orders_by_date_range(
    restaurant_id: int, start_time: int, end_time: int
):
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders_by_date_range(
            restaurant_id, username, start_time, end_time
        )
        return orders
    except ValueError as err:
        raise convert_service_error(err)


@router.get(
    "/restaurants/{restaurant_id}/orders/filter/status-and-date",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
async def get_restaurant_orders_by_status_and_date(
    restaurant_id: int, order_status: str, start_time: int, end_time: int
):
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders_by_status_and_date(
            restaurant_id, username, order_status, start_time, end_time
        )
        return orders
    except ValueError as err:
        raise convert_service_error(err)
