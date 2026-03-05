from src.services.payment_service import PaymentService
from src.schemas.order_schema import Order, PaymentStatus, OrderStatus
from src.schemas.customer_schema import Customer
import pytest

# Creating helper objects so that I don't have to rewrite the shit every time
def create_customer():
    return Customer(
        name="Trevor",
        login="trevor123",
        password="pass",
        email="twuchic123@gmail.com",
        paymentType="credit card",
        paymentdetails="1234567812345678",
        pastorders=[]
    )

def create_order():
    return Order(
        items=[],
        cost=25.0,
        resturant="Joe's pizza",
        customer="Trevor",
        time=67,
        cusine="Italian",
        distance=5.0
    )

# The system shall validate payment details
def test_validate_payment_success():

    customer = create_customer()

    result = PaymentService.validate_payment(customer)

    assert result is True


# The payment fails for invalid details
def test_validate_payment_invalid_card():

    customer = create_customer()
    customer.paymentdetails = "abcd"

    result = PaymentService.validate_payment(customer)

    assert result is False

# The system processes payment and updates both the order and payment status
def test_process_payment_update_status():
    
    customer = create_customer()
    order = create_order()

    update_order = PaymentService.process_payment(order, customer)

    # We check both possibilities as we used RNG to determine outcome
    assert update_order.payment_status in[
        PaymentStatus.ACCEPTED,
        PaymentStatus.REJECTED
    ]

    assert update_order.order_status in [
        OrderStatus.CONFIRMED,
        OrderStatus.PAYMENT_REJECTED
    ]

# Each order is processed only once (to prevent processing payment multiple times)
def test_duplicate_payment_prevention():
    
    customer = create_customer()
    order = create_order()

    order.payment_status = PaymentStatus.ACCEPTED

    with pytest.raises(Exception):
        PaymentService.process_payment(order, customer)

# The system allows customer to retry after failed payment
def test_retry_payment_after_failed_payment():

    customer = create_customer()
    order = create_order()

    order.payment_status = PaymentStatus.REJECTED

    updated_order = PaymentService.process_payment(order,customer)

    assert updated_order.payment_status in [
        PaymentStatus.ACCEPTED,
        PaymentStatus.REJECTED
    ]