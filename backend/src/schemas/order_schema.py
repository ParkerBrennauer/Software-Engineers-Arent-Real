from enum import Enum
from pydantic import BaseModel


class OrderStatus(str, Enum):
    CREATED = "created"
    PAYMENT_PENDING = "payment pending"
    PAYMENT_REJECTED = "payment rejected"
    PAYMENT_ACCEPTED = "payment accepted"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready for pickup"
    PICKED_UP = "picked up"
    OUT_FOR_DELIVERY = "out for delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


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

class OrderCreate(BaseModel):
    items: list
    cost: float
    restaurant: str
    customer: str
    time: int
    cuisine: str
    distance: float


class OrderUpdate(BaseModel):
    items: list | None = None
    cost: float | None = None
    restaurant: str | None = None
    customer: str | None = None
    time: int | None = None
    cuisine: str | None = None
    distance: float | None = None

    order_status: OrderStatus | None = None
    delay_reason: str | None = None

    driver: str | None = None
