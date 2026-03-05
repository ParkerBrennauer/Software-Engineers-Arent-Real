from fastapi import HTTPException
from repositories.deliveries_repo import get_order, update_rating
from schemas.ratings import RatingCreate


def submit_rating(order_id: str, payload: RatingCreate):
    
    # Check if order is there
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Make sure we don't create duplicate ratings
    if order["submitted_stars"] is not None:
        raise HTTPException(
            status_code=400,
            detail="This order has already been rated"
        )

    updated_order = update_rating(order_id, payload.stars)

    return {
        "order_id": order_id,
        "stars": payload.stars
    }