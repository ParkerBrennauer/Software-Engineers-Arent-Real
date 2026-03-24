from src.repositories.rating_repo import RatingRepo
from src.schemas.rating_schema import RatingCreate, RatingResponse


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
