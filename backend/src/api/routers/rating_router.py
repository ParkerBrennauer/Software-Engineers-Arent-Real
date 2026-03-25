from fastapi import APIRouter, HTTPException, Query, status

from src.schemas.rating_schema import RatingCreate, RatingResponse
from src.schemas.review_schema import (
    DeleteResponse,
    FeedbackPromptResponse,
    FilteredReviewsResponse,
    ReportCreate,
    ReportResponse,
    ReviewCreate,
    ReviewEdit,
    ReviewEditResponse,
    ReviewResponse,
)
from src.services.rating_service import RatingService

router = APIRouter(prefix="/orders", tags=["ratings"])


def _raise_rating_error(err: ValueError) -> None:
    message = str(err)
    if message in {
        "Order not found",
        "Restaurant not found",
        "Restaurant not found for this order",
    }:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        ) from err
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    ) from err


@router.post(
    "/{order_id}/rating",
    response_model=RatingResponse,
    status_code=status.HTTP_200_OK,
)
async def rate_order(order_id: str, payload: RatingCreate):
    try:
        return await RatingService.submit_rating(order_id, payload)
    except ValueError as err:
        _raise_rating_error(err)


@router.post(
    "/{order_id}/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def review_order(order_id: str, payload: ReviewCreate):
    try:
        return await RatingService.submit_review(order_id, payload)
    except ValueError as err:
        _raise_rating_error(err)


@router.put(
    "/{order_id}/review",
    response_model=ReviewEditResponse,
    status_code=status.HTTP_200_OK,
)
async def edit_review(order_id: str, payload: ReviewEdit):
    try:
        return await RatingService.edit_order_review(order_id, payload)
    except ValueError as err:
        _raise_rating_error(err)


@router.delete(
    "/{order_id}/review",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_review(order_id: str):
    try:
        return await RatingService.delete_order_review(order_id)
    except ValueError as err:
        _raise_rating_error(err)


@router.get(
    "/{order_id}/feedback-prompt",
    response_model=FeedbackPromptResponse,
    status_code=status.HTTP_200_OK,
)
async def feedback_prompt(order_id: str):
    try:
        return await RatingService.check_feedback_prompt(order_id)
    except ValueError as err:
        _raise_rating_error(err)


@router.get(
    "/restaurants/{restaurant_id}/reviews",
    response_model=FilteredReviewsResponse,
    status_code=status.HTTP_200_OK,
)
async def filter_reviews(
    restaurant_id: int,
    stars: int | None = Query(None, ge=1, le=5),
):
    try:
        return await RatingService.get_filtered_reviews(restaurant_id, stars=stars)
    except ValueError as err:
        _raise_rating_error(err)


@router.post(
    "/{order_id}/report",
    response_model=ReportResponse,
    status_code=status.HTTP_200_OK,
)
async def report_review(order_id: str, payload: ReportCreate):
    try:
        return await RatingService.submit_report(order_id, payload)
    except ValueError as err:
        _raise_rating_error(err)
