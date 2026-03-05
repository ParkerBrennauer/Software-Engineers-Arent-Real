from pydantic import BaseModel


class Order(BaseModel):
    items: list
    cost: float
    resturant: str
    customer: str
    time: int
    cusine: str
    distance: float


class OrderCreate(BaseModel):
    items: list
    cost: float
    resturant: str
    customer: str
    time: int
    cusine: str
    distance: float


class OrderUpdate(BaseModel):
    items: list
    cost: float
    resturant: str
    customer: str
    time: int
    cusine: str
    distance: float


class Item(BaseModel):

    itemName: str
    cost: float
    cusine: str
    time: int
    resturant: str
