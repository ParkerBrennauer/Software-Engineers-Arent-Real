from fastapi import APIRouter, status
from src.schemas.order_schema import OrderCreate, OrderUpdate
from src.schemas.order_tracking_schema import OrderTrackingResponse, OrderTrackingStatusUpdate
from src.models.order_model import OrderInternal
from src.services.order_services import OrderService
from src.services.order_tracking_service import OrderTrackingService
from src.api.dependencies import convert_service_error
router = APIRouter(prefix='/orders', tags=['orders'])

@router.post('/place', response_model=OrderInternal, status_code=status.HTTP_201_CREATED)
async def place_order(order: OrderCreate):
    try:
        return await OrderService.create_order(order)
    except ValueError as err:
        raise convert_service_error(err)

@router.post('/{order_id}/items', response_model=OrderInternal, status_code=status.HTTP_200_OK)
async def add_items_to_order(order_id: str, items_update: OrderUpdate):
    try:
        return await OrderService.update_order(int(order_id), {'items': items_update.items})
    except ValueError as err:
        raise convert_service_error(err)

@router.get('/{order_id}')
async def get_order_status(order_id: str):
    return await OrderService.get_order_status(order_id)

@router.get('/restaurant/{restaurant}')
async def get_restaurant_orders(restaurant: str):
    return await OrderService.get_restaurant_orders(restaurant)

@router.put('/{order_id}/cancel')
async def cancel_order(order_id: str):
    return await OrderService.cancel_order(order_id)

@router.put('/{order_id}/ready')
async def mark_ready(order_id: str):
    return await OrderService.mark_ready_for_pickup(order_id)

@router.put('/{order_id}/restaurant-delay')
async def restaurant_delay(order_id: str, reason: str):
    return await OrderService.report_restaurant_delay(order_id, reason)

@router.get('/driver/{driver}')
async def get_driver_orders(driver: str):
    return await OrderService.get_driver_orders(driver)

@router.put('/{order_id}/pickup')
async def pickup_order(order_id: str):
    return await OrderService.pickup_order(order_id)

@router.put('/{order_id}/driver-delay')
async def driver_delay(order_id: str, reason: str):
    return await OrderService.report_driver_delay(order_id, reason)

@router.put('/{order_id}/assign-driver')
async def assign_driver(order_id: str, driver: str):
    return await OrderService.assign_driver(order_id, driver)

@router.put('/{order_id}/refund')
async def refund_order(order_id: str):
    return await OrderService.process_refund(order_id)

@router.get('/{order_id}/tracking', response_model=OrderTrackingResponse, status_code=status.HTTP_200_OK)
async def get_order_tracking(order_id: str):
    try:
        return await OrderTrackingService.get_tracking_info(order_id)
    except ValueError as err:
        raise convert_service_error(err)

@router.post('/{order_id}/tracking/refresh', response_model=OrderTrackingResponse, status_code=status.HTTP_200_OK)
async def refresh_order_tracking(order_id: str):
    try:
        return await OrderTrackingService.refresh_tracking(order_id)
    except ValueError as err:
        raise convert_service_error(err)

@router.patch('/{order_id}/tracking/status', response_model=OrderTrackingResponse, status_code=status.HTTP_200_OK)
async def update_order_tracking_status(order_id: str, tracking_update: OrderTrackingStatusUpdate):
    try:
        return await OrderTrackingService.update_tracking_status(order_id, tracking_update)
    except ValueError as err:
        raise convert_service_error(err)
