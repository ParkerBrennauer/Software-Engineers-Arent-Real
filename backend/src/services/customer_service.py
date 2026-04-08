from src.services.order_services import OrderService

class CustomerService:

    @staticmethod
    async def get_order_history(username: str) -> list:
        if not username:
            raise ValueError('No username submitted')
        return await OrderService.get_previous_orders_by_user(username)
