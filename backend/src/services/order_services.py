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
        restaurant_order = []
        for _, order_data in orders.items():
            if order_data.get("restaurant") == restaurant:
                restaurant_order.append(Order(**order_data))
        return restaurant_order

    @staticmethod
    async def cancel_order(order_id: str) -> Order:

        update = OrderUpdate(order_status=OrderStatus.CANCELLED)
        return await OrderRepo.update_order(order_id, update)
