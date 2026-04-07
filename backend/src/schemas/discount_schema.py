from pydantic import BaseModel


class DiscountCreate(BaseModel):
    discount_rate: float
    discount_name: str
    restaurant_id: int


class DiscountApply(BaseModel):
    order_total: float
    discount_code: str