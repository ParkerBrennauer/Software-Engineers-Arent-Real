from src.services.payment_service import PaymentService
from src.schemas.order_schema import Order, PaymentStatus, OrderStatus
from src.schemas.customer_schema import CustomerRegister
import pytest
from pydantic import ValidationError

def create_customer():
    return CustomerRegister(name='Trevor', username='trevor123', password='pass', email='twuchic123@gmail.com', payment_type='credit card', payment_details='1234567812345678')

def create_order():
    return Order(items=[], cost=25.0, restaurant="Joe's pizza", customer='Trevor', time=20, cuisine='Italian', distance=5.0)

@pytest.mark.asyncio
async def test_validate_payment_details():
    customer = create_customer()
    assert customer.payment_details == '1234567812345678'

@pytest.mark.asyncio
async def test_invalid_card():
    with pytest.raises(ValidationError):
        CustomerRegister(name='Trevor', username='trevor123', password='pass', email='twuchic123@gmail.com', payment_type='credit card', payment_details='abcd')

@pytest.mark.asyncio
async def test_process_payment_accept_simulation():
    order = create_order()
    updated_order = await PaymentService.process_payment(
        order, card_digits='4111111111111111', simulate='accept'
    )
    assert updated_order.payment_status == PaymentStatus.ACCEPTED
    assert updated_order.order_status == OrderStatus.CONFIRMED

@pytest.mark.asyncio
async def test_process_payment_reject_simulation():
    order = create_order()
    updated_order = await PaymentService.process_payment(
        order, card_digits='4111111111111111', simulate='reject'
    )
    assert updated_order.payment_status == PaymentStatus.REJECTED
    assert updated_order.order_status == OrderStatus.PAYMENT_REJECTED
    assert updated_order.payment_rejection_reason

@pytest.mark.asyncio
async def test_process_payment_auto_accepts_any_valid_16_digit_card():
    for card in ('4111111111111112', '4111111111111111'):
        order = create_order()
        updated = await PaymentService.process_payment(order, card_digits=card, simulate='auto')
        assert updated.payment_status == PaymentStatus.ACCEPTED

@pytest.mark.asyncio
async def test_process_payment_auto_accepts_15_digit_card():
    order = create_order()
    updated_order = await PaymentService.process_payment(
        order, card_digits='411111111111111', simulate='auto'
    )
    assert updated_order.payment_status == PaymentStatus.ACCEPTED

@pytest.mark.asyncio
async def test_duplicate_payment_prevention():
    order = create_order()
    order.payment_status = PaymentStatus.ACCEPTED
    with pytest.raises(Exception):
        await PaymentService.process_payment(order, card_digits='4111111111111112', simulate='auto')

@pytest.mark.asyncio
async def test_retry_payment_after_failed_payment():
    order = create_order()
    order.payment_status = PaymentStatus.REJECTED
    updated_order = await PaymentService.process_payment(
        order, card_digits='4111111111111112', simulate='accept'
    )
    assert updated_order.payment_status == PaymentStatus.ACCEPTED
