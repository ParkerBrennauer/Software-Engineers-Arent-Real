from src.schemas.order_schema import OrderCreate
from src.models.order_model import OrderInternal
from src.repositories.order_repo import OrderRepo


class OrderService:

    @staticmethod
    async def create_order(create_order: OrderCreate) -> dict:
        order_data = create_order.model_dump()
        order_data["order_status"] = "payment pending"
        order_data["payment_status"] = "pending"

        largest_order_id = await OrderRepo.get_largest_order_id()
        order_data["id"] = largest_order_id + 1 if largest_order_id is not None else 1

        order_data["locked"] = False
        order_data["items"] = order_data.get("items", [])
        order_data["cost"] = await OrderService.calculate_order_cost(order_data["items"])

        saved_data = await OrderRepo.save_order(order_data)
        return OrderInternal.model_validate(saved_data)

    @staticmethod
    async def update_order(order_id: int, update_data: dict) -> dict:
        order_id = int(order_id)
        existing_order = await OrderRepo.get_by_id(order_id)

        if existing_order is None:
            existing_order = {}

        if existing_order.get("locked"):
            raise ValueError("Order is locked and cannot be updated")

        updated_order = {**existing_order, **update_data}
        updated_order["items"] = update_data.get("items", existing_order.get("items", []))
        updated_order["cost"] = await OrderService.calculate_order_cost(updated_order["items"])

        saved_order = await OrderRepo.update_order(order_id, updated_order)
        return OrderInternal.model_validate(saved_order)

    @staticmethod
    async def calculate_order_cost(items: list) -> float:
        total = 0.0
        for item in items:
            total += item.get("price", 0)

        total = total * 1.13
        return round(total, 2)

    @staticmethod
    async def lock_order(order_id: int) -> OrderInternal:
        order_id = int(order_id)
        existing_order = await OrderRepo.get_by_id(order_id)

        if existing_order is None:
            existing_order = {}

        if existing_order.get("locked"):
            return OrderInternal.model_validate(existing_order)

        updated_order = {**existing_order, "locked": True}
        saved_data = await OrderRepo.update_order(order_id, updated_order)

        return OrderInternal.model_validate(saved_data)

    @staticmethod
    async def get_order_status(order_id: int):
        order_id = int(order_id)
        existing_order = await OrderRepo.get_by_id(order_id)

        if existing_order is None:
            existing_order = {}
        return existing_order

    @staticmethod
    async def cancel_order(order_id: int):
        order_id = int(order_id)
        return await OrderService.update_order(order_id, {
            "order_status": "cancelled"
        })

    @staticmethod
    async def mark_ready_for_pickup(order_id: int):
        order_id = int(order_id)
        return await OrderService.update_order(order_id, {
            "order_status": "ready_for_pickup"
        })

    @staticmethod
    async def assign_driver(order_id: int, driver: str):
        order_id = int(order_id)
        return await OrderService.update_order(order_id, {
            "driver": driver
        })

    @staticmethod
    async def get_driver_orders(driver: str):
        return await OrderRepo.get_orders_by_driver(driver)

    @staticmethod
    async def pickup_order(order_id: int):
        order_id = int(order_id)
        return await OrderService.update_order(order_id, {
            "order_status": "picked_up"
        })

    @staticmethod
    async def report_restaurant_delay(order_id: int, reason: str):
        order_id = int(order_id)
        updated = await OrderService.update_order(order_id, {
            "order_status": "delayed",
            "delay_reason": reason
        })

        if "cancel" in reason.lower() or "cannot prepare" in reason.lower():
            return await OrderService.process_refund(order_id)

        return updated

    @staticmethod
    async def report_driver_delay(order_id: int, reason: str):
        order_id = int(order_id)
        return await OrderService.update_order(order_id, {
            "order_status": "delayed",
            "delay_reason": reason
        })

    @staticmethod
    async def process_refund(order_id: int):
        order_id = int(order_id)
        order = await OrderRepo.get_by_id(order_id)

        if order is None:
            order = {}

        if order.get("refund_issued"):
            raise ValueError("Refund already issued")

        if order.get("order_status") not in ["delayed", "cancelled"]:
            raise ValueError("Refund not applicable")

        if order.get("payment_status") != "accepted":
            raise ValueError("Cannot refund unpaid order")

        updated_order = {
            **order,
            "refund_issued": True,
            "refund_amount": order.get("cost", 0)
        }

        saved = await OrderRepo.update_order(order_id, updated_order)
        return OrderInternal.model_validate(saved)
