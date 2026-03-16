from pydantic import BaseModel
from src.schemas.item_schema import ItemBase
from src.schemas.order_schema import Order


class Item(BaseModel):
    restaurant_id: int
    item_name: str
    cost: float
    cuisine: str
    restaurant: str
    avg_rating: float


class Restaurant(BaseModel):
    # name: str
    restaurant_id: int
    menu: list[ItemBase]
    cuisine: str
    ratings: dict
    orders: list[Order]


class RestaurantCreate(BaseModel):
    # name: str
    menu: list[ItemBase]
    cuisine: str
    ratings: dict[str, float]
    orders: list[Order]


class RestaurantUpdate(BaseModel):
    # name: str
    menu: list[ItemBase] | None = None
    cuisine: str | None = None
