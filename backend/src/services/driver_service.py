from src.schemas.order_schema import Order
from src.services.order_services import OrderService

class DriverService():

    @staticmethod
    async def tip_driver(order_id: int):
        order = await OrderService.get_order_status(order_id)

        if not order:
            raise ValueError("Order not found")

        if isinstance(order, Order):
            order = order.model_dump()

        tip = order.get("tip_amount", 0)

        if tip <= 0:
            raise ValueError("No tip to pay out")

        if order.get("tip_paid"):
            raise ValueError("Tip already paid")

        driver = order.get("driver")

        if not driver:
            raise ValueError("No driver assigned to order")

        await OrderService.update_order(order_id, {"tip_paid": True})

        return {
            "status": "paid",
            "driver": driver,
            "amount": tip
        }
