from src.services.driver_service import DriverService

class TipService:

    @staticmethod
    def calculate_tip(subtotal: float, tip_percent: float = None, tip_amount: float = None) -> float:
        if tip_percent is not None and tip_amount is not None:
            raise ValueError("Provide either a tip percent or tip amount, not both")

        if tip_percent is not None:
            if tip_percent < 0:
                raise ValueError("Tip percent cannot be negative")
            return round(subtotal * (tip_percent/100), 2)

        if tip_amount is not None:
            if tip_amount < 0:
                raise ValueError("Tip amount cannot be negative")
            return round(tip_amount, 2)

        raise ValueError("Must provide tip_percent or tip_amount")

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

        return updated
