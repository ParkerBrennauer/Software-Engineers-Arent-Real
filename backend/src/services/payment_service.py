from src.schemas.order_schema import PaymentStatus, OrderStatus, Order

# Below is to make pylint happy
# pylint: disable=too-few-public-methods
class PaymentService:

    @staticmethod
    async def process_payment(order: Order) -> Order:

        if order.payment_status == PaymentStatus.ACCEPTED:
            raise ValueError("Payment already successfully processed.")
        order.payment_status = PaymentStatus.ACCEPTED
        order.order_status = OrderStatus.CONFIRMED

        return order
