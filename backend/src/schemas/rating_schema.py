from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    stars: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    order_id: str
    stars: int
