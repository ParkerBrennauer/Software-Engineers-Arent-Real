from enum import Enum
from pydantic import BaseModel

# Enum for keeping track of the order status and payment status
class OrderStatus(str, Enum):
    CREATED = "created"
    PAYMENT_PENDING = "payment pending"
    PAYMENT_REJECTED = "payment rejected"
    PAYMENT_ACCEPTED = "payment accepted"
    CONFIRMED = "confirmed"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Order(BaseModel):
    items: list
    cost: float
    resturant: str
    customer: str
    time: int
    cusine: str
    distance: float

    order_status: OrderStatus = OrderStatus.PAYMENT_PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING


class OrderCreate(BaseModel):
    items: list
    cost: float
    resturant: str
    customer: str
    time: int
    cusine: str
    distance: float


class OrderUpdate(BaseModel):
    items: list
    cost: float
    resturant: str
    customer: str
    time: int
    cusine: str
    distance: float


class Item(BaseModel):

    itemName: str
    cost: float
    cusine: str
    time: int
    resturant: str
