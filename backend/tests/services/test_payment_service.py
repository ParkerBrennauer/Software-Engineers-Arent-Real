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
async def test_process_payment_update_status():
    order = create_order()
    updated_order = await PaymentService.process_payment(order)
    assert updated_order.payment_status in [PaymentStatus.ACCEPTED, PaymentStatus.REJECTED]
    assert updated_order.order_status in [OrderStatus.CONFIRMED, OrderStatus.PAYMENT_REJECTED]

@pytest.mark.asyncio
async def test_duplicate_payment_prevention():
    order = create_order()
    order.payment_status = PaymentStatus.ACCEPTED
    with pytest.raises(Exception):
        await PaymentService.process_payment(order)

@pytest.mark.asyncio
async def test_retry_payment_after_failed_payment():
    order = create_order()
    order.payment_status = PaymentStatus.REJECTED
    updated_order = await PaymentService.process_payment(order)
    assert updated_order.payment_status in [PaymentStatus.ACCEPTED, PaymentStatus.REJECTED]
