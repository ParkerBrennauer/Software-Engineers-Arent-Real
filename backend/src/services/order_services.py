from src.schemas.order_schema import Order, OrderStatus, OrderUpdate
from src.repositories.order_repo import OrderRepo

class OrderService:

    @staticmethod
    async def get_order_status(order_id: str) -> Order:

        order = await OrderRepo.get_order(order_id)
        return order

    @staticmethod
    async def get_restaurant_orders(restaurant: str) -> list[Order]:

        orders = await OrderRepo.get_all_orders()
        restaurant_orders = []
        for _, order_data in orders.items():
            if order_data.get("restaurant") == restaurant:
                restaurant_orders.append(Order(**order_data))
        return restaurant_orders

    @staticmethod
    async def mark_ready_for_pickup(order_id: str) -> Order:

        update = OrderUpdate(order_status=OrderStatus.READY_FOR_PICKUP)
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def report_restaurant_delay(order_id: str, reason: str) -> Order:

        update = OrderUpdate(
            order_status = OrderStatus.DELAYED,
            delay_reason = reason
        )
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def get_driver_orders(driver : str) -> list[Order]:

        return await OrderRepo.get_orders_by_driver(driver)

    @staticmethod
    async def pickup_order(order_id: str) -> Order:

        update = OrderUpdate(order_status=OrderStatus.PICKED_UP)
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def report_driver_delay(order_id: str, reason: str) -> Order:

        update = OrderUpdate(
            order_status = OrderStatus.DELAYED,
            delay_reason = reason
        )
        return await OrderRepo.update_order(order_id, update)

    @staticmethod
    async def cancel_order(order_id: str) -> Order:

        update = OrderUpdate(order_status=OrderStatus.CANCELLED)
        return await OrderRepo.update_order(order_id, update)
