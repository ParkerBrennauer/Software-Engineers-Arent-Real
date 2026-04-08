from typing import Optional
from pydantic import BaseModel

class ItemRestrictions(BaseModel):
    vegan: bool = False
    vegetarian: bool = False
    gluten_free: bool = False
    dairy_free: bool = False
    nut_free: bool = False
    halal: bool = False
    kosher: bool = False

class ItemBase(BaseModel):
    item_name: str
    restaurant_id: int
    cost: float
    cuisine: str
    times_ordered: int
    avg_rating: float
    dietary: ItemRestrictions = ItemRestrictions()

class ItemCreate(ItemBase):
    item_name: str
    restaurant_id: int
    cost: float
    cuisine: str
    times_ordered: float = 0
    avg_rating: float = 0.0
    dietary: ItemRestrictions = ItemRestrictions()

class ItemUpdate(BaseModel):
    item_name: Optional[str] = None
    cost: Optional[float] = None
    cuisine: Optional[str] = None
    dietary: Optional[ItemRestrictions] = None

class ItemUpdateAnalytics(BaseModel):
    times_ordered: int
    avg_rating: float
