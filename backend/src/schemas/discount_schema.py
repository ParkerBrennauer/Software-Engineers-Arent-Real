from pydantic import BaseModel

class DiscountApply(BaseModel):
    order_total: float
    discount_code: str

class DiscountCreate(BaseModel):
    discount_rate: float
    discount_code: str
    restaurant_id: int