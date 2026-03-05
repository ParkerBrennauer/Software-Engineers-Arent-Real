from fastapi import APIRouter
from schemas.ratings import RatingCreate, RatingResponse
from services.rating_service import submit_rating

router = APIRouter(prefix="/orders", tags=["ratings"])


@router.post("/{order_id}/rating", response_model=RatingResponse)
def rate_order(order_id: str, payload: RatingCreate):
    return submit_rating(order_id, payload)
