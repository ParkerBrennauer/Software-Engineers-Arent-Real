from src.repositories.rating_repo import RatingRepo
from src.schemas.rating_schema import RatingCreate, RatingResponse
from src.schemas.review_schema import ReviewCreate, ReviewResponse


class RatingService:
    @staticmethod
    async def submit_rating(
        order_id: str, payload: RatingCreate
    ) -> RatingResponse:
        order = await RatingRepo.get_by_order_id(order_id)

        if order is None:
            raise ValueError("Order not found")

        if order.get("submitted_stars") is not None:
            raise ValueError("This order has already been rated")

        updated_order = await RatingRepo.update_submitted_rating(
            order_id,
            payload.stars,
        )
        if not updated_order:
            raise ValueError("Order not found")

        return RatingResponse(
            order_id=order_id,
            stars=payload.stars,
        )

    @staticmethod
    async def submit_review(
        order_id: str, payload: ReviewCreate
    ) -> ReviewResponse:
        order = await RatingRepo.get_by_order_id(order_id)

        if order is None:
            raise ValueError("Order not found")

        if order.get("review_text") is not None:
            raise ValueError("This order has already been reviewed")

        restaurant_id = await RatingRepo.get_restaurant_id_by_order_id(order_id)
        if restaurant_id is None:
            raise ValueError("Restaurant not found for this order")

        updated_order = await RatingRepo.update_review_text(
            order_id,
            payload.review_text,
        )
        if not updated_order:
            raise ValueError("Order not found")

        return ReviewResponse(
            order_id=order_id,
            restaurant_id=restaurant_id,
            review_text=payload.review_text,
        )
