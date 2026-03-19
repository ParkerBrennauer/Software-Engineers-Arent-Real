from fastapi import HTTPException
from repositories.deliveries_repo import (
    get_order, update_rating, update_review,
    get_restaurant_by_order, edit_review, delete_review
)
from schemas.ratings_schema import RatingCreate, ReviewCreate, ReviewEdit


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


def edit_order_review(order_id: str, payload: ReviewEdit):
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order["submitted_stars"] is None and order.get("review_text") is None:
        raise HTTPException(
            status_code=400,
            detail="No review exists to edit for this order"
        )

    if payload.stars is None and payload.review_text is None:
        raise HTTPException(
            status_code=400,
            detail="Nothing to update"
        )

    updated = edit_review(
        order_id,
        stars=payload.stars,
        review_text=payload.review_text
    )

    return {
        "order_id": order_id,
        "submitted_stars": updated["submitted_stars"],
        "review_text": updated.get("review_text")
    }


def delete_order_review(order_id: str):
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order["submitted_stars"] is None and order.get("review_text") is None:
        raise HTTPException(
            status_code=400,
            detail="No review exists to delete for this order"
        )

    delete_review(order_id)

    return {
        "order_id": order_id,
        "message": "Review and rating deleted successfully"
    }


def check_feedback_prompt(order_id: str):
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "order_id": order_id,
        "prompt_feedback": True,
        "message": "How was your order? Leave a rating and review!"
    }
