from src.services.order_services import OrderService

class TipService:

    @staticmethod
    def calculate_tip(subtotal: float, tip_percent: float=None, tip_amount: float=None) -> float:
        if tip_percent is not None and tip_amount is not None:
            raise ValueError('Provide either a tip percent or tip amount, not both')
        if tip_percent is not None:
            if tip_percent < 0:
                raise ValueError('Tip percent cannot be negative')
            return round(subtotal * (tip_percent / 100), 2)
        if tip_amount is not None:
            if tip_amount < 0:
                raise ValueError('Tip amount cannot be negative')
            return round(tip_amount, 2)
        raise ValueError('Must provide tip_percent or tip_amount')

    @staticmethod
    async def apply_tip(order_id: int, tip_percent: float=None, tip_amount: float=None):
        order = await OrderService.get_order_status(order_id)
        if not order:
            raise ValueError('Order not found')
        subtotal = order['cost']
        final_tip = TipService.calculate_tip(subtotal, tip_percent=tip_percent, tip_amount=tip_amount)
        updated = await OrderService.update_order(order_id, {'tip_percent': tip_percent, 'tip_amount': final_tip, 'tip_paid': False})
        return updated
