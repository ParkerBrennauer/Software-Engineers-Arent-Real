from fastapi import APIRouter
from schemas.rating_schema import RatingCreate, RatingResponse
from schemas.review_schema import ReviewCreate, ReviewResponse
from services.rating_service import submit_rating, submit_review

router = APIRouter(prefix="/orders", tags=["ratings"])


@router.post("/{order_id}/rating", response_model=RatingResponse)
def rate_order(order_id: str, payload: RatingCreate):
    return submit_rating(order_id, payload)


@router.post("/{order_id}/review", response_model=ReviewResponse)
def review_order(order_id: str, payload: ReviewCreate):
    return submit_review(order_id, payload)
