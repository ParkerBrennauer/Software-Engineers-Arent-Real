from pydantic import BaseModel
from typing import List
from src.schemas.order_schema import Order

class Item(BaseModel):
    restaurantId: int
    itemName: str
    cost: float
    cuisine: str
    restaurant: str
    avg_rating: float

class Restaurant(BaseModel):
    #name: str
    restaurantId: int
    menu: List[Item]
    cuisine: str
    ratings: dict
    orders: List[Order]

class RestaurantCreate(BaseModel):
    #name: str
    menu: List[Item]
    cuisine: str
    ratings: dict
    orders: List[Order]

class RestaurantUpdate(BaseModel):
    #name: str
    menu: List[Item]
    cuisine: str

