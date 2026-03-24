import pytest
from pydantic import ValidationError

from src.repositories.rating_repo import RatingRepo
from src.schemas.review_schema import ReviewCreate, ReviewEdit
from src.services.rating_service import RatingService


@pytest.mark.asyncio
async def test_submit_review_success(monkeypatch):
    order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 5,
    }
    captured = {}

    async def fake_get_by_order_id(_order_id: str):
        return dict(order)

    async def fake_get_restaurant_id_by_order_id(_order_id: str):
        return 16

    async def fake_update_review_text(order_id: str, review_text: str):
        captured["order_id"] = order_id
        captured["review_text"] = review_text
        return {**order, "review_text": review_text}

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(
        RatingRepo,
        "get_restaurant_id_by_order_id",
        fake_get_restaurant_id_by_order_id,
    )
    monkeypatch.setattr(
        RatingRepo,
        "update_review_text",
        fake_update_review_text,
    )

    result = await RatingService.submit_review(
        "1d8e87M",
        ReviewCreate(review_text="Great food, fast delivery!"),
    )

    assert result.order_id == "1d8e87M"
    assert result.restaurant_id == 16
    assert result.review_text == "Great food, fast delivery!"
    assert captured == {
        "order_id": "1d8e87M",
        "review_text": "Great food, fast delivery!",
    }


@pytest.mark.asyncio
async def test_submit_review_order_not_found(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)

    with pytest.raises(ValueError, match="Order not found"):
        await RatingService.submit_review(
            "FAKE_ORDER_ID",
            ReviewCreate(review_text="Great food!"),
        )


@pytest.mark.asyncio
async def test_submit_review_already_reviewed(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return {"review_text": "Already wrote a review"}

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)

    with pytest.raises(ValueError, match="This order has already been reviewed"):
        await RatingService.submit_review(
            "1d8e87M",
            ReviewCreate(review_text="Trying again"),
        )


@pytest.mark.asyncio
async def test_submit_review_restaurant_not_found(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return {"review_text": None}

    async def fake_get_restaurant_id_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(
        RatingRepo,
        "get_restaurant_id_by_order_id",
        fake_get_restaurant_id_by_order_id,
    )

    with pytest.raises(ValueError, match="Restaurant not found for this order"):
        await RatingService.submit_review(
            "1d8e87M",
            ReviewCreate(review_text="Great food!"),
        )


@pytest.mark.asyncio
async def test_review_schema_rejects_empty_text():
    with pytest.raises(ValidationError):
        ReviewCreate(review_text="")


@pytest.mark.asyncio
async def test_review_schema_accepts_valid_text():
    review = ReviewCreate(review_text="Food was amazing!")
    assert review.review_text == "Food was amazing!"


@pytest.mark.asyncio
async def test_edit_review_update_both(monkeypatch):
    order = {
        "submitted_stars": 4,
        "review_text": "Pretty good food",
    }

    async def fake_get_by_order_id(_order_id: str):
        return dict(order)

    async def fake_update_review_fields(
        _order_id: str,
        stars: int | None = None,
        review_text: str | None = None,
    ):
        return {
            "submitted_stars": stars,
            "review_text": review_text,
        }

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(
        RatingRepo,
        "update_review_fields",
        fake_update_review_fields,
    )

    result = await RatingService.edit_order_review(
        "1d8e87M",
        ReviewEdit(stars=5, review_text="Updated review"),
    )

    assert result.order_id == "1d8e87M"
    assert result.submitted_stars == 5
    assert result.review_text == "Updated review"


@pytest.mark.asyncio
async def test_edit_review_update_stars_only(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return {
            "submitted_stars": 4,
            "review_text": "Pretty good food",
        }

    async def fake_update_review_fields(
        _order_id: str,
        stars: int | None = None,
        review_text: str | None = None,
    ):
        return {
            "submitted_stars": stars,
            "review_text": "Pretty good food" if review_text is None else review_text,
        }

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(
        RatingRepo,
        "update_review_fields",
        fake_update_review_fields,
    )

    result = await RatingService.edit_order_review(
        "1d8e87M",
        ReviewEdit(stars=2),
    )

    assert result.submitted_stars == 2
    assert result.review_text == "Pretty good food"


@pytest.mark.asyncio
async def test_edit_review_order_not_found(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)

    with pytest.raises(ValueError, match="Order not found"):
        await RatingService.edit_order_review(
            "FAKE_ID",
            ReviewEdit(stars=3),
        )


@pytest.mark.asyncio
async def test_edit_review_no_existing_review(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return {
            "submitted_stars": None,
            "review_text": None,
        }

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)

    with pytest.raises(ValueError, match="No review exists to edit for this order"):
        await RatingService.edit_order_review(
            "1d8e87M",
            ReviewEdit(stars=3),
        )


@pytest.mark.asyncio
async def test_edit_review_nothing_to_update(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return {
            "submitted_stars": 4,
            "review_text": "Pretty good food",
        }

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)

    with pytest.raises(ValueError, match="Nothing to update"):
        await RatingService.edit_order_review("1d8e87M", ReviewEdit())


@pytest.mark.asyncio
async def test_delete_review_success(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return {
            "submitted_stars": 4,
            "review_text": "Pretty good food",
        }

    async def fake_delete_review(_order_id: str):
        return {
            "submitted_stars": None,
            "review_text": None,
        }

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, "delete_review", fake_delete_review)

    result = await RatingService.delete_order_review("1d8e87M")

    assert result.order_id == "1d8e87M"
    assert result.message == "Review and rating deleted successfully"


@pytest.mark.asyncio
async def test_delete_review_order_not_found(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)

    with pytest.raises(ValueError, match="Order not found"):
        await RatingService.delete_order_review("FAKE_ID")


@pytest.mark.asyncio
async def test_delete_review_nothing_to_delete(monkeypatch):
    async def fake_get_by_order_id(_order_id: str):
        return {
            "submitted_stars": None,
            "review_text": None,
        }

    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)

    with pytest.raises(ValueError, match="No review exists to delete for this order"):
        await RatingService.delete_order_review("1d8e87M")
