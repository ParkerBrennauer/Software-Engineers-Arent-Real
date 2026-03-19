from typing import Optional, List
from enum import Enum
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


class FeedbackPromptResponse(BaseModel):
    order_id: str
    prompt_feedback: bool
    message: str


class FilteredReview(BaseModel):
    order_id: str
    submitted_stars: Optional[int]
    review_text: Optional[str]


class FilteredReviewsResponse(BaseModel):
    restaurant_id: int
    stars_filter: Optional[int]
    total_reviews: int
    reviews: List[FilteredReview]


class ReportReason(str, Enum):
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate_language"
    OTHER = "other"


class ReportCreate(BaseModel):
    reason: ReportReason
    description: Optional[str] = Field(
        None, max_length=500
    )


class ReportResponse(BaseModel):
    report_id: int
    order_id: str
    reason: ReportReason
    description: Optional[str]
    message: str
