from src.schemas.order_schema import Order, OrderStatus, OrderUpdate, PaymentStatus
from src.repositories.order_repo import OrderRepo

class OrderService:

    @staticmethod
    async def get_order_status(order_id: str) -> Order:

        order = await OrderRepo.get_order(order_id)
        return order

    @staticmethod
    async def get_restaurant_orders(restaurant: str) -> list[Order]:

        orders = await OrderRepo.get_all_orders()
        restaurant_order = []
        for _, order_data in orders.items():
            if order_data.get("restaurant") == restaurant:
                restaurant_order.append(Order(**order_data))
        return restaurant_order

    @staticmethod
    async def cancel_order(order_id: str) -> Order:

        update = OrderUpdate(order_status=OrderStatus.CANCELLED)
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def mark_ready_for_pickup(order_id: str) -> Order:

        update = OrderUpdate(order_status=OrderStatus.READY_FOR_PICKUP)
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def report_restaurant_delay(order_id: str, reason: str) -> Order:

        await OrderRepo.get_order(order_id)
        update = OrderUpdate(
            order_status= OrderStatus.DELAYED,
            delay_reason= reason
        )
        updated_order = await OrderRepo.update_order(order_id, update)
        if "cancel" in reason.lower() or "cannot prepare" in reason.lower():
            updated_order = await OrderService.process_refund(order_id)
        return updated_order

    @staticmethod
    async def assign_driver(order_id: str, driver: str) -> Order:

        update = OrderUpdate(driver=driver)
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def get_driver_orders(driver: str) -> list[Order]:

        return await OrderRepo.get_orders_by_driver(driver)

    @staticmethod
    async def pickup_order(order_id: str) -> Order:

        update = OrderUpdate(order_status=OrderStatus.PICKED_UP)
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def report_driver_delay(order_id: str, reason: str) -> Order:

        update = OrderUpdate(
            order_status= OrderStatus.DELAYED,
            delay_reason= reason
        )
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def process_refund(order_id: str) -> Order:

        order = await OrderRepo.get_order(order_id)

        if order.refund_issued:
            raise ValueError("Refund already issued")

        if order.order_status not in [OrderStatus.DELAYED, OrderStatus.CANCELLED]:
            raise ValueError("Refund not applicable")

        if order.payment_status != PaymentStatus.ACCEPTED:
            raise ValueError("Cannot refund unpaid order")

        update = OrderUpdate(
            refund_issued=True,
            refund_amount=order.cost
        )
        return await OrderRepo.update_order(order_id, update)
