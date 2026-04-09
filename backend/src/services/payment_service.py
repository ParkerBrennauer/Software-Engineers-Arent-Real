from src.schemas.order_schema import PaymentStatus, OrderStatus, Order

class PaymentService:

    SIMULATION_STEPS = ('validate_instrument', 'authorize', 'capture')

    @staticmethod
    async def process_payment(
        order: Order,
        *,
        card_digits: str,
        simulate: str = 'auto',
    ) -> Order:
        if order.payment_status == PaymentStatus.ACCEPTED:
            raise ValueError('Payment already successfully processed.')
        digits = ''.join(ch for ch in str(card_digits) if ch.isdigit())
        if len(digits) not in (15, 16):
            raise ValueError('Payment details must be a valid 15–16 digit card number.')

        steps = list(PaymentService.SIMULATION_STEPS)
        order.payment_simulation_steps = steps

        if simulate == 'reject':
            accepted = False
            reject_reason = 'Payment was declined by the simulated processor (forced reject).'
        else:
            accepted = True
            reject_reason = None

        if accepted:
            order.payment_status = PaymentStatus.ACCEPTED
            order.order_status = OrderStatus.CONFIRMED
            order.payment_rejection_reason = None
        else:
            order.payment_status = PaymentStatus.REJECTED
            order.order_status = OrderStatus.PAYMENT_REJECTED
            order.payment_rejection_reason = reject_reason

        return order
