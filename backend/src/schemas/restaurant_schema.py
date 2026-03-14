from pydantic import BaseModel
from src.schemas.order_schema import Order


class Item(BaseModel):
    restaurant_id: int
    item_name: str
    cost: float
    cuisine: str
    restaurant: str
    avg_rating: float


class Restaurant(BaseModel):
    restaurant_id: int
    menu: list[Item]
    cuisine: str
    ratings: dict
    orders: list[Order]


class RestaurantCreate(BaseModel):
    menu: list[Item]
    cuisine: str
    ratings: dict[str, float]
    orders: list[Order]


class RestaurantUpdate(BaseModel):
    menu: list[Item] | None = None
    cuisine: str | None = None
