from src.services.payment_service import PaymentService
from src.schemas.order_schema import Order, PaymentStatus, OrderStatus
from src.schemas.customer_schema import Customer
import pytest
from pydantic import ValidationError

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
        time=20,
        cusine="Italian",
        distance=5.0
    )

# The system shall validate payment details (by checking customer creation)
@pytest.mark.asyncio
async def test_validate_payment_details():

    customer = create_customer()

    assert customer.paymentdetails == "1234567812345678"


# The payment fails for invalid details
@pytest.mark.asyncio
async def test_invalid_card():

    with pytest.raises(ValidationError):

        Customer(
            name="Trevor",
            login="trevor123",
            password="pass",
            email="twuchic123@gmail.com",
            paymentType="credit card",
            paymentdetails="abcd",
            pastorders=[]
        )

# The system processes payment and updates both the order and payment status
@pytest.mark.asyncio
async def test_process_payment_update_status():

    order = create_order()

    updated_order = await PaymentService.process_payment(order)

    # We check both possibilities as we used RNG to determine outcome
    assert updated_order.payment_status in[
        PaymentStatus.ACCEPTED,
        PaymentStatus.REJECTED
    ]

    assert updated_order.order_status in [
        OrderStatus.CONFIRMED,
        OrderStatus.PAYMENT_REJECTED
    ]

# Each order is processed only once (to prevent processing payment multiple times)
@pytest.mark.asyncio
async def test_duplicate_payment_prevention():

    order = create_order()

    order.payment_status = PaymentStatus.ACCEPTED

    with pytest.raises(Exception):
        await PaymentService.process_payment(order)

# The system allows customer to retry after failed payment
@pytest.mark.asyncio
async def test_retry_payment_after_failed_payment():

    order = create_order()

    order.payment_status = PaymentStatus.REJECTED

    updated_order = await PaymentService.process_payment(order)

    assert updated_order.payment_status in [
        PaymentStatus.ACCEPTED,
        PaymentStatus.REJECTED
    ]
