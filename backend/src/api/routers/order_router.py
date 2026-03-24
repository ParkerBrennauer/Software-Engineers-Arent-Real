from fastapi import APIRouter, HTTPException, status

from src.schemas.order_tracking_schema import (
    OrderTrackingResponse,
    OrderTrackingStatusUpdate,
)
from src.services.order_tracking_service import OrderTrackingService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    "/{order_id}/tracking",
    response_model=OrderTrackingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_order_tracking(order_id: str):
    try:
        return await OrderTrackingService.get_tracking_info(order_id)
    except ValueError as err:
        message = str(err)
        if message == "Order not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from err


@router.post(
    "/{order_id}/tracking/refresh",
    response_model=OrderTrackingResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_order_tracking(order_id: str):
    try:
        return await OrderTrackingService.refresh_tracking(order_id)
    except ValueError as err:
        message = str(err)
        if message == "Order not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from err


@router.patch(
    "/{order_id}/tracking/status",
    response_model=OrderTrackingResponse,
    status_code=status.HTTP_200_OK,
)
async def update_order_tracking_status(
    order_id: str, tracking_update: OrderTrackingStatusUpdate
):
    try:
        return await OrderTrackingService.update_tracking_status(
            order_id,
            tracking_update,
        )
    except ValueError as err:
        message = str(err)
        if message == "Order not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from err
