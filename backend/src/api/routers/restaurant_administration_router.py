from fastapi import APIRouter, HTTPException, status

from src.schemas.user_schema import UserResponse
from src.schemas.order_schema import Order
from src.services.restaurant_owner_services import RestaurantOwnerService
from src.schemas.restaurant_owner_schema import (
    RestaurantOwnerAssignStaffRequest as StaffAssignmentRequest,
)

router = APIRouter(
    prefix="/restaurant_administration", tags=["users", "restaurant_administration"]
)


@router.post(
    "/{owner_username}/staff",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def assign_staff(owner_username: str, body: StaffAssignmentRequest):
    try:
        updated_user = await RestaurantOwnerService.assign_user_as_staff(
            owner_username,
            body.staff_username,
        )
        return updated_user
    except ValueError as err:
        message = str(err)
        if message in ["Owner not found", "User not found"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        if message == "User is not a restaurant owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err


@router.get(
    "/restaurants/{restaurant_id}/orders",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
async def get_restaurant_orders(restaurant_id: int, username: str):
    try:
        orders = await RestaurantOwnerService.get_restaurant_orders(restaurant_id, username)
        return orders
    except ValueError as err:
        message = str(err)
        if message in ["User not found", "Restaurant not found"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        if "does not have permission" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err
