from enum import Enum
from typing import Literal
from pydantic import BaseModel

class OrderStatus(str, Enum):
    CREATED = 'created'
    PAYMENT_PENDING = 'payment pending'
    PAYMENT_REJECTED = 'payment rejected'
    PAYMENT_ACCEPTED = 'payment accepted'
    CONFIRMED = 'confirmed'
    PREPARING = 'preparing'
    READY_FOR_PICKUP = 'ready for pickup'
    PICKED_UP = 'picked up'
    OUT_FOR_DELIVERY = 'out for delivery'
    DELIVERED = 'delivered'
    DELAYED = 'delayed'
    CANCELLED = 'cancelled'

class PaymentStatus(str, Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

class Order(BaseModel):
    items: list
    cost: float
    restaurant: str
    customer: str
    time: int
    cuisine: str
    distance: float
    order_status: OrderStatus = OrderStatus.PAYMENT_PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    delay_reason: str | None = None
    driver: str | None = None
    delivery_instructions: str | None = None
    refund_issued: bool = False
    refund_amount: float | None = None
    payment_rejection_reason: str | None = None
    payment_simulation_steps: list[str] | None = None
    id: int | None = None
    tip_percent: float | None = None
    tip_amount: float | None = None
    tip_paid: bool = False
    sig_delay_refund_done: bool = False

class OrderCreate(BaseModel):
    items: list
    cost: float = 0.0
    restaurant: str
    customer: str
    time: int
    cuisine: str
    distance: float | None = None
    delivery_instructions: str | None = None

class PaymentAttemptRequest(BaseModel):

    simulate: Literal['auto', 'accept', 'reject'] = 'auto'

class OrderUpdate(BaseModel):
    items: list | None = None
    cost: float | None = None
    restaurant: str | None = None
    customer: str | None = None
    time: int | None = None
    cuisine: str | None = None
    distance: float | None = None
    delivery_instructions: str | None = None
    order_status: OrderStatus | None = None
    delay_reason: str | None = None
    driver: str | None = None
