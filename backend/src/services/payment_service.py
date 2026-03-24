import random
from src.schemas.order_schema import PaymentStatus, OrderStatus, Order

# Below is to make pylint happy
# pylint: disable=too-few-public-methods
class PaymentService:

    # Payment processing
    @staticmethod
    async def process_payment(order: Order) -> Order:

        # Checking if the payment has already been processed
        if order.payment_status == PaymentStatus.ACCEPTED:
            raise ValueError("Payment already successfully processed.")

        # Simulate payment process by using random.
        approved = random.choice([True, False])

        if approved:
            order.payment_status = PaymentStatus.ACCEPTED
            order.order_status = OrderStatus.CONFIRMED
        else:
            order.payment_status = PaymentStatus.REJECTED
            order.order_status = OrderStatus.PAYMENT_REJECTED

        return order
