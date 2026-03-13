from fastapi import APIRouter
from src.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("orders/{order_id}")
async def get_order_status(order_id: str):

    order = await OrderService.get_order_status(order_id)
    return order

@router.get("/restaurant/{restaurant}")
async def get_restaurant_orders(restaurant: str):

    orders = await OrderService.get_restaurant_orders(restaurant)
    return None

@router.put("/{order_id}/ready")
async def mark_ready(order_id: str):

    order = await OrderService.mark_ready_for_pickup(order_id)
    return order

@router.put("/{order_id}/restaurant_delay")
async def restaurant_delay(order_id: str, reason: str):

    order = await OrderService.report_restaurant_delay(order_id, reason)
    return order