from src.schemas.order_schema import OrderCreate
from src.models.order_model import OrderInternal
from src.repositories import OrderRepo

class OrderService:
    @staticmethod
    async def create_order(create_order: OrderCreate) -> dict:

        order_data = create_order.model_dump()
        order_data["order_status"] = "payment pending"
        order_data["payment_status"] = "pending"

        largest_order_id = await OrderRepo.get_largest_order_id()
        if largest_order_id is not None:
            order_data["id"] = largest_order_id + 1
        else:
            order_data["id"] = 1

        order_data["locked"] = False
        order_data["items"] = order_data.get("items", [])
        order_data["total_cost"] = await OrderService.calculate_order_cost(order_data["items"])

        saved_data = await OrderRepo.save_order(order_data)


        return OrderInternal.model_validate(saved_data)

    @staticmethod
    async def update_order(order_id: int, update_data: dict) -> dict:
        existing_order = await OrderRepo.get_by_id(order_id)
        if not existing_order:
            raise ValueError("Order not found")

        if existing_order.get("locked"):
            raise ValueError("Order is locked and cannot be updated")

        updated_order = {**existing_order, **update_data}

        updated_order["items"] = update_data.get("items", existing_order.get("items", []))
        updated_order["total_cost"] = await OrderService.calculate_order_cost(updated_order["items"])

        saved_order = await OrderRepo.update_order(order_id, updated_order)

        return OrderInternal.model_validate(saved_order)

    @staticmethod
    async def calculate_order_cost(items: list) -> float:
        total = 0.0
        for item in items:
            total += item.get("price", 0)

        total = total * 1.13

        return total

    @staticmethod
    async def lock_order(order_id: int) -> OrderInternal:
        existing_order = await OrderRepo.get_by_id(order_id)

        if not existing_order:
            raise ValueError("Order not found")

        if existing_order.get("locked"):
            return OrderInternal.model_validate(existing_order)

        updated_order = {**existing_order, "locked": True}

        saved_data = await OrderRepo.update_order(order_id, updated_order)

        return OrderInternal.model_validate(saved_data)