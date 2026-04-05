from src.schemas.order_schema import Order
from src.repositories.order_repo import OrderRepo

class DriverService():

    @staticmethod
    async def tip_driver(order_id: int):
        order = await OrderRepo.get_order(order_id)

        if not order:
            raise ValueError("Order not found")

        if isinstance(order, Order):
            order = order.model_dump()

        tip = order.get("tip_amount", 0)

        if tip <= 0:
            raise ValueError("No tip to pay out")

        print(f"Paying driver {order.get('driver')} tip: {tip}")

        return {"status": "paid", "driver": order.get("driver"), "amount": tip}
