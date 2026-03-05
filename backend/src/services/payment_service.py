import random
from src.schemas.order_schema import PaymentStatus, OrderStatus, Order
from src.schemas.customer_schema import Customer

class PaymentService:

    # Validating customer's payment details
    @staticmethod
    def validate_payment(customer : Customer) -> bool:

        if not customer.paymentdetails.isdigit():
            return False
        if len(customer.paymentdetails) != 16:
            return False
        if (customer.paymentType.lower() not in ["credit card", "debit card"]):
            return False
        
        return True

    # Payment processing
    @staticmethod
    def process_payment(order: Order, customer: Customer) -> Order:
    
        # Checking if the payment has already been processed
        if order.payment_status == PaymentStatus.ACCEPTED:
            raise Exception("Payment already successfully processed.")

        # Validate payment details
        if not PaymentService.validate_payment(customer):
            order.payment_status = PaymentStatus.REJECTED
            order.order_status = OrderStatus.PAYMENT_REJECTED
            return order

        # Simulate payment process by using random.
        approved = random.choice([True, False])

        if approved:
            order.payment_status = PaymentStatus.ACCEPTED
            order.order_status = OrderStatus.CONFIRMED
        else:
            order.payment_status = PaymentStatus.REJECTED
            order.order_status = OrderStatus.PAYMENT_REJECTED

        return order