from src.services.driver_service import DriverService

class TipService:

    @staticmethod
    def calculate_tip(subtotal: float, tip_percent: float) -> float:
        if tip_percent < 0:
            raise ValueError("Tip percent cannot be negative")

        return round(subtotal * (tip_percent/100), 2)

    @staticmethod
    async def apply_tip(order_id: int, tip_percent: float):
        from src.services.order_services import OrderService

        order = await OrderService.get_order_status(order_id)

        subtotal = order["cost"]
        tip_amount = TipService.calculate_tip(subtotal, tip_percent)

        updated = await OrderService.update_order(
            order_id,
            {
                "tip_percent": tip_percent,
                "tip_amount": tip_amount
            }
        )

        await DriverService.tip_driver(order_id)

        return updated
