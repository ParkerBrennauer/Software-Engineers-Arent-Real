from fastapi import HTTPException
from repositories.deliveries_repo import (
    get_order, update_rating, update_review,
    get_restaurant_by_order, edit_review, delete_review,
    get_restaurant_reviews, create_report
)
from schemas.ratings_schema import (
    RatingCreate, ReviewCreate, ReviewEdit, ReportCreate
)


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


def get_filtered_reviews(restaurant_id: int, stars: int = None):
    reviews = get_restaurant_reviews(restaurant_id, stars=stars)

    if reviews is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return {
        "restaurant_id": restaurant_id,
        "stars_filter": stars,
        "total_reviews": len(reviews),
        "reviews": reviews
    }


def submit_report(order_id: str, payload: ReportCreate):
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    has_review = (
        order.get("submitted_stars") is not None
        or order.get("review_text") is not None
    )

    if not has_review:
        raise HTTPException(
            status_code=400,
            detail="No review exists to report for this order"
        )

    report = create_report(
        order_id,
        reason=payload.reason.value,
        description=payload.description
    )

    return {
        "report_id": report["report_id"],
        "order_id": order_id,
        "reason": payload.reason,
        "description": payload.description,
        "message": "Report submitted successfully"
    }
