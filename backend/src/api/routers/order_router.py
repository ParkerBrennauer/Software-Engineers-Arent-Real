from fastapi import APIRouter
from src.schemas.order_schema import Order
from src.services.order_service import OrderService

router = APIRouter()

@router.get("orders/{order_id}")
async def get_order_status(order_id: str):

    order = await OrderService.get_order_status(order_id)
    return order

async def get_all_orders(restaurant: str):

    return None



# Work on this after finish implementing order_service.py
