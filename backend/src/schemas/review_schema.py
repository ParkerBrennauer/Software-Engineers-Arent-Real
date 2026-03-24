from typing import Optional
from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    review_text: str = Field(..., min_length=1, max_length=1000)


class ReviewResponse(BaseModel):
    order_id: str
    restaurant_id: int
    review_text: str


class ReviewEdit(BaseModel):
    stars: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, min_length=1, max_length=1000)


class ReviewEditResponse(BaseModel):
    order_id: str
    submitted_stars: Optional[int]
    review_text: Optional[str]


class DeleteResponse(BaseModel):
    order_id: str
    message: str
