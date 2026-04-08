from fastapi import APIRouter, status
from src.schemas.user_schema import UserResponse
from src.schemas.order_schema import Order
from src.services.restaurant_owner_services import RestaurantOwnerService
from src.schemas.restaurant_owner_schema import RestaurantOwnerAssignStaffRequest as StaffAssignmentRequest
from src.api.dependencies import convert_service_error
router = APIRouter(prefix='/restaurant_administration', tags=['users', 'restaurant_administration'])

@router.post('/{owner_username}/staff', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def assign_staff(owner_username: str, body: StaffAssignmentRequest):
    try:
        updated_user = await RestaurantOwnerService.assign_user_as_staff(owner_username, body.staff_username)
        return updated_user
    except ValueError as err:
        raise convert_service_error(err)

@router.get('/restaurants/{restaurant_id}/orders', response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_restaurant_orders(restaurant_id: int, username: str):
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders(restaurant_id, username)
        return orders
    except ValueError as err:
        raise convert_service_error(err)

@router.get('/restaurants/{restaurant_id}/orders/filter/status', response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_restaurant_orders_by_status(restaurant_id: int, username: str, order_status: str):
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders_by_status(restaurant_id, username, order_status)
        return orders
    except ValueError as err:
        raise convert_service_error(err)

@router.get('/restaurants/{restaurant_id}/orders/filter/date', response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_restaurant_orders_by_date_range(restaurant_id: int, username: str, start_time: int, end_time: int):
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders_by_date_range(restaurant_id, username, start_time, end_time)
        return orders
    except ValueError as err:
        raise convert_service_error(err)

@router.get('/restaurants/{restaurant_id}/orders/filter/status-and-date', response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_restaurant_orders_by_status_and_date(restaurant_id: int, username: str, order_status: str, start_time: int, end_time: int):
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders_by_status_and_date(restaurant_id, username, order_status, start_time, end_time)
        return orders
    except ValueError as err:
        raise convert_service_error(err)
