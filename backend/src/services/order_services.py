from src.schemas.order.schema import OrderCreate
from src.models.order_model import OrderInternal
from src.repositories import OrderRepo

class order_services:
    @staticmethod
    async def create_order(create_order: OrderCreate) -> dict:

        order_data = create_order.model_dump()
        order_data["order_status"] = "payment pending"
        order_data["payment_status"] = "pending"
        order_data["id"] = 0 #placeholder for id generation

        saved_data = await OrderRepo.save_order(order_data)

        return OrderInternal.model_validate(saved_data)

    @staticmethod
    async def update_order(order_id: int, update_data: dict) -> dict:
        existing_order = await OrderRepo.get_by_id(order_id)
        if not existing_order:
            raise ValueError("Order not found")
