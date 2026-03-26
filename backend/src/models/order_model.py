from pydantic import BaseModel

class OrderInternal(BaseModel):
    id: int
    restaurant: str
    customer: str
    time: int
    cuisine: str
    distance: float
    order_status: str
    payment_status: str
    items: list
    cost: float
    locked: bool = False
    delay_reason: str | None = None
    driver: str | None = None