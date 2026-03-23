from fastapi import APIRouter
from src.services.order_services import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/{order_id}")
async def get_order_status(order_id: str):

    order = await OrderService.get_order_status(order_id)
    return order

@router.get("/restaurant/{restaurant}")
async def get_restaurant_orders(restaurant: str):

    orders = await OrderService.get_restaurant_orders(restaurant)
    return orders

@router.put("/{order_id}/cancel")
async def cancel_order(order_id: str):

    order = await OrderService.cancel_order(order_id)
    return order
