from fastapi import APIRouter
from schemas.ratings_schema import (
    RatingCreate, RatingResponse,
    ReviewCreate, ReviewResponse,
    ReviewEdit, ReviewEditResponse,
    DeleteResponse, FeedbackPromptResponse
)
from services.rating_service import (
    submit_rating, submit_review,
    edit_order_review, delete_order_review,
    check_feedback_prompt
)

router = APIRouter(prefix="/orders", tags=["ratings"])


@router.post("/{order_id}/rating", response_model=RatingResponse)
def rate_order(order_id: str, payload: RatingCreate):
    return submit_rating(order_id, payload)


@router.post("/{order_id}/review", response_model=ReviewResponse)
def review_order(order_id: str, payload: ReviewCreate):
    return submit_review(order_id, payload)


@router.put("/{order_id}/review", response_model=ReviewEditResponse)
def edit_review(order_id: str, payload: ReviewEdit):
    return edit_order_review(order_id, payload)


@router.delete("/{order_id}/review", response_model=DeleteResponse)
def delete_review(order_id: str):
    return delete_order_review(order_id)


@router.get("/{order_id}/feedback-prompt", response_model=FeedbackPromptResponse)
def feedback_prompt(order_id: str):
    return check_feedback_prompt(order_id)
