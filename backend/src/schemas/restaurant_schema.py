from pydantic import BaseModel
from src.schemas.item_schema import ItemBase
from src.schemas.order_schema import Order

class Restaurant(BaseModel):
    restaurant_id: int
    menu: list[ItemBase]
    cuisine: str
    ratings: dict
    orders: list[Order]


class RestaurantCreate(BaseModel):
    menu: list[ItemBase]
    cuisine: str
    ratings: dict[str, float]
    orders: list[Order]


class RestaurantUpdate(BaseModel):
    menu: list[ItemBase] | None = None
    cuisine: str | None = None
