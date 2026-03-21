from fastapi import HTTPException
from repositories.deliveries_repo import (
    get_order, update_rating, update_review, get_restaurant_by_order
)
from schemas.rating_schema import RatingCreate
from schemas.review_schema import ReviewCreate


def submit_rating(order_id: str, payload: RatingCreate):
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order["submitted_stars"] is not None:
        raise HTTPException(
            status_code=400,
            detail="This order has already been rated"
        )

    update_rating(order_id, payload.stars)

    return {
        "order_id": order_id,
        "stars": payload.stars
    }


def submit_review(order_id: str, payload: ReviewCreate):
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.get("review_text") is not None:
        raise HTTPException(
            status_code=400,
            detail="This order has already been reviewed"
        )

    restaurant_id = get_restaurant_by_order(order_id)

    if restaurant_id is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found for this order"
        )

    update_review(order_id, payload.review_text)

    return {
        "order_id": order_id,
        "restaurant_id": restaurant_id,
        "review_text": payload.review_text
    }
