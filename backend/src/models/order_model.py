from src.schemas.order_schema import Order

class OrderInternal(Order):
    id: int
    order_status: str
    payment_status: str
    items: list
    cost : float
    locked : bool = False
