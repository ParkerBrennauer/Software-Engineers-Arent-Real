from pydantic import BaseModel

class OrderInternal(BaseModel):
    id: int
    order_status: str
    payment_status: str
    items: list
    cost: float
    locked: bool = False
    delivery_instructions: str | None = None
    tip_percent: float | None = None
    tip_amount: float | None = None
    tip_paid: bool = False
