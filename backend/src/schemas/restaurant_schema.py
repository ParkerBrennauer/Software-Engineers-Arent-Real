from typing import List, Optional
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
    menu: list[ItemBase] = []
    cuisine: str
    ratings: dict = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, }
    orders: list[Order] = []


class RestaurantUpdate(BaseModel):
    menu: Optional[list[ItemBase]] = None
    cuisine: Optional[str] = None


class RestaurantSearchAdvanced(BaseModel):
    query: str
    filters: List[str] = []
    sort: str = ""
