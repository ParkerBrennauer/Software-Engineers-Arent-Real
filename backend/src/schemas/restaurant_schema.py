from typing import List
from pydantic import BaseModel
from backend.src.schemas.item_schema import Item
from backend.src.schemas.order_schema import Order

class Restaurant(BaseModel):
    # name: str
    restaurantId: int
    menu: List[Item]
    cuisine: str
    ratings: dict
    orders: List[Order]


class RestaurantCreate(BaseModel):
    # name: str
    menu: List[Item]
    cuisine: str
    ratings: dict
    orders: List[Order]


class RestaurantUpdate(BaseModel):
    # name: str
    menu: List[Item]
    cuisine: str
