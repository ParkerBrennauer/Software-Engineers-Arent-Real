from src.repositories.rating_repo import RatingRepo
from src.schemas.rating_schema import RatingCreate, RatingResponse
from src.schemas.review_schema import (
    DeleteResponse,
    FeedbackPromptResponse,
    FilteredReviewsResponse,
    ReviewCreate,
    ReviewEdit,
    ReviewEditResponse,
    ReviewResponse,
)


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

    @staticmethod
    async def edit_order_review(
        order_id: str, payload: ReviewEdit
    ) -> ReviewEditResponse:
        order = await RatingRepo.get_by_order_id(order_id)

        if order is None:
            raise ValueError("Order not found")

        if (
            order.get("submitted_stars") is None
            and order.get("review_text") is None
        ):
            raise ValueError("No review exists to edit for this order")

        if payload.stars is None and payload.review_text is None:
            raise ValueError("Nothing to update")

        updated_order = await RatingRepo.update_review_fields(
            order_id,
            stars=payload.stars,
            review_text=payload.review_text,
        )
        if not updated_order:
            raise ValueError("Order not found")

        return ReviewEditResponse(
            order_id=order_id,
            submitted_stars=updated_order.get("submitted_stars"),
            review_text=updated_order.get("review_text"),
        )

    @staticmethod
    async def delete_order_review(order_id: str) -> DeleteResponse:
        order = await RatingRepo.get_by_order_id(order_id)

        if order is None:
            raise ValueError("Order not found")

        if (
            order.get("submitted_stars") is None
            and order.get("review_text") is None
        ):
            raise ValueError("No review exists to delete for this order")

        deleted_order = await RatingRepo.delete_review(order_id)
        if not deleted_order:
            raise ValueError("Order not found")

        return DeleteResponse(
            order_id=order_id,
            message="Review and rating deleted successfully",
        )

    @staticmethod
    async def check_feedback_prompt(order_id: str) -> FeedbackPromptResponse:
        order = await RatingRepo.get_by_order_id(order_id)

        if order is None:
            raise ValueError("Order not found")

        return FeedbackPromptResponse(
            order_id=order_id,
            prompt_feedback=True,
            message="How was your order? Leave a rating and review!",
        )

    @staticmethod
    async def get_filtered_reviews(
        restaurant_id: int,
        stars: int | None = None,
    ) -> FilteredReviewsResponse:
        reviews = await RatingRepo.get_restaurant_reviews(
            restaurant_id,
            stars=stars,
        )

        if reviews is None:
            raise ValueError("Restaurant not found")

        return FilteredReviewsResponse(
            restaurant_id=restaurant_id,
            stars_filter=stars,
            total_reviews=len(reviews),
            reviews=reviews,
        )
