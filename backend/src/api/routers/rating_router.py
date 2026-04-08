from fastapi import APIRouter, Query, status
from src.schemas.rating_schema import RatingCreate, RatingResponse
from src.schemas.review_schema import DeleteResponse, FeedbackPromptResponse, FilteredReviewsResponse, ReportCreate, ReportResponse, ReviewCreate, ReviewEdit, ReviewEditResponse, ReviewResponse
from src.services.rating_service import RatingService
from src.services.user_service import UserService
from src.api.dependencies import convert_service_error
from src.repositories.rating_repo import RatingRepo

router = APIRouter(prefix='/orders', tags=['ratings'])

@router.post('/{order_id}/rating', response_model=RatingResponse, status_code=status.HTTP_200_OK)
async def rate_order(order_id: str, payload: RatingCreate):
    current_user = UserService.get_current_user()
    if not current_user:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        order = await RatingRepo.get_by_order_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.get('customer') != current_user:
            raise ValueError("User does not have permission to rate this order")
        return await RatingService.submit_rating(order_id, payload)
    except ValueError as err:
        raise convert_service_error(err)

@router.post('/{order_id}/review', response_model=ReviewResponse, status_code=status.HTTP_200_OK)
async def review_order(order_id: str, payload: ReviewCreate):
    current_user = UserService.get_current_user()
    if not current_user:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        order = await RatingRepo.get_by_order_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.get('customer') != current_user:
            raise ValueError("User does not have permission to review this order")
        return await RatingService.submit_review(order_id, payload)
    except ValueError as err:
        raise convert_service_error(err)

@router.put('/{order_id}/review', response_model=ReviewEditResponse, status_code=status.HTTP_200_OK)
async def edit_review(order_id: str, payload: ReviewEdit):
    current_user = UserService.get_current_user()
    if not current_user:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        order = await RatingRepo.get_by_order_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.get('customer') != current_user:
            raise ValueError("User does not have permission to edit this review")
        return await RatingService.edit_order_review(order_id, payload)
    except ValueError as err:
        raise convert_service_error(err)

@router.delete('/{order_id}/review', response_model=DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_review(order_id: str):
    current_user = UserService.get_current_user()
    if not current_user:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        order = await RatingRepo.get_by_order_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.get('customer') != current_user:
            raise ValueError("User does not have permission to delete this review")
        return await RatingService.delete_order_review(order_id)
    except ValueError as err:
        raise convert_service_error(err)

@router.get('/{order_id}/feedback-prompt', response_model=FeedbackPromptResponse, status_code=status.HTTP_200_OK)
async def feedback_prompt(order_id: str):
    try:
        return await RatingService.check_feedback_prompt(order_id)
    except ValueError as err:
        raise convert_service_error(err)

@router.get('/restaurants/{restaurant_id}/reviews', response_model=FilteredReviewsResponse, status_code=status.HTTP_200_OK)
async def filter_reviews(restaurant_id: int, stars: int | None=Query(None, ge=1, le=5)):
    try:
        return await RatingService.get_filtered_reviews(restaurant_id, stars=stars)
    except ValueError as err:
        raise convert_service_error(err)

@router.post('/{order_id}/report', response_model=ReportResponse, status_code=status.HTTP_200_OK)
async def report_review(order_id: str, payload: ReportCreate):
    current_user = UserService.get_current_user()
    if not current_user:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        order = await RatingRepo.get_by_order_id(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.get('customer') != current_user:
            raise ValueError("User does not have permission to report this review")
        return await RatingService.submit_report(order_id, payload)
    except ValueError as err:
        raise convert_service_error(err)
