from pydantic import BaseModel

class Discount_Internal(BaseModel):
    resturant_id: int
    discount_rate: int
    owner_account: str
