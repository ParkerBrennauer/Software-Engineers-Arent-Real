from fastapi import APIRouter, HTTPException
from src.services.order_services import OrderService
from src.schemas.order_schema import OrderCreate, OrderUpdate
from src.services.order_services import OrderService
from src.repositories import OrderRepo
from src.models.order_model import OrderInternal

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderInternal)
async def create_order(order: OrderCreate):
    try:
        return await OrderService.create_order(order)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}")
async def get_order(order_id: int):
    order = await OrderRepo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/")
async def get_all_orders():
    return await OrderRepo.read_all()


@router.put("/{order_id}", response_model=OrderInternal)
async def update_order(order_id: int, order_update: OrderUpdate):
    try:
        update_data = order_update.model_dump(exclude_unset=True)
        return await OrderService.update_order(order_id, update_data)
    except ValueError as e:
        if str(e) == "Order not found":
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{order_id}/lock", response_model=OrderInternal)
async def lock_order(order_id: int):
    try:
        return await OrderService.lock_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/orders/{order_id}")
async def get_order_status(order_id: int):
    order = await OrderService.get_order_status(order_id)

    if not order:
        return None

    return {
        "order_id": str(order_id),
        "status": order.get("order_status")
    }

@router.get("/restaurant/{restaurant}")
async def get_restaurant_orders(restaurant: str):

    orders = await OrderService.get_restaurant_orders(restaurant)
    return orders

@router.put("/{order_id}/cancel")
async def cancel_order(order_id: str):

    order = await OrderService.cancel_order(order_id)
    return order

@router.put("/{order_id}/ready")
async def mark_ready(order_id: str):

    order = await OrderService.mark_ready_for_pickup(order_id)
    return order

@router.put("/{order_id}/restaurant-delay")
async def restaurant_delay(order_id: str, reason: str):

    order = await OrderService.report_restaurant_delay(order_id, reason)
    return order

@router.get("/driver/{driver}")
async def get_driver_orders(driver: str):

    orders = await OrderService.get_driver_orders(driver)
    return orders

@router.put("/{order_id}/pickup")
async def pickup_order(order_id: str):

    order = await OrderService.pickup_order(order_id)
    return order

@router.put("/{order_id}/driver-delay")
async def driver_delay(order_id: str, reason: str):

    order = await OrderService.report_driver_delay(order_id, reason)
    return order

@router.put("/{order_id}/assign-driver")
async def assign_driver(order_id: str, driver: str):

    return await OrderService.assign_driver(order_id, driver)

@router.put("/{order_id}/refund")
async def refund_order(order_id: str):

    return await OrderService.process_refund(order_id)

@router.get("/customer/{username}")
async def get_orders_for_customer(username: str):
    return await OrderRepo.get_by_customer_username(username)