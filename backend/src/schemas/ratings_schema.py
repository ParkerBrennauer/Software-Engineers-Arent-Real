from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    stars: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    order_id: str
    stars: int


class ReviewCreate(BaseModel):
    review_text: str = Field(..., min_length=1, max_length=1000)


class ReviewResponse(BaseModel):
    order_id: str
    restaurant_id: int
    review_text: str
