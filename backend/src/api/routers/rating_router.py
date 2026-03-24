from fastapi import APIRouter, HTTPException, status

from src.schemas.rating_schema import RatingCreate, RatingResponse
from src.schemas.review_schema import ReviewCreate, ReviewResponse
from src.services.rating_service import RatingService

router = APIRouter(prefix="/orders", tags=["ratings"])


@router.post(
    "/{order_id}/rating",
    response_model=RatingResponse,
    status_code=status.HTTP_200_OK,
)
async def rate_order(order_id: str, payload: RatingCreate):
    try:
        return await RatingService.submit_rating(order_id, payload)
    except ValueError as err:
        message = str(err)
        if message == "Order not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from err
        if message == "Restaurant not found for this order":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from err


@router.post(
    "/{order_id}/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def review_order(order_id: str, payload: ReviewCreate):
    try:
        return await RatingService.submit_review(order_id, payload)
    except ValueError as err:
        message = str(err)
        if message == "Order not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from err
        if message == "Restaurant not found for this order":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from err
