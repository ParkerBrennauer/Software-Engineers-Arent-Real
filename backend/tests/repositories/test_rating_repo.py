import json

import pytest

from src.repositories.order_repo import OrderRepo
from src.repositories.rating_repo import RatingRepo


@pytest.mark.asyncio
async def test_update_submitted_rating_creates_review_entry_from_order(
    monkeypatch, tmp_path
):
    reviews_file = tmp_path / "reviews.json"
    reviews_file.write_text("{}")
    monkeypatch.setattr(RatingRepo, "FILE_PATH", reviews_file)

    async def fake_get_by_id(order_id: str):
        assert order_id == "10008"
        return {
            "id": 10008,
            "customer": "gcheem04",
            "restaurant": "Restaurant_16",
            "order_status": "payment pending",
        }

    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    updated = await RatingRepo.update_submitted_rating("10008", 5)

    assert updated == {
        "customer": "gcheem04",
        "restaurant": "Restaurant_16",
        "submitted_stars": 5,
        "review_text": None,
    }
    stored = json.loads(reviews_file.read_text())
    assert stored["10008"] == updated


@pytest.mark.asyncio
async def test_get_restaurant_id_by_order_id_falls_back_to_order_data(
    monkeypatch, tmp_path
):
    restaurants_file = tmp_path / "restaurants.json"
    restaurants_file.write_text("{}")
    monkeypatch.setattr(RatingRepo, "RESTAURANTS_FILE_PATH", restaurants_file)

    async def fake_get_by_id(order_id: str):
        assert order_id == "10009"
        return {
            "id": 10009,
            "customer": "gcheem04",
            "restaurant": "Restaurant_16",
        }

    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    restaurant_id = await RatingRepo.get_restaurant_id_by_order_id("10009")

    assert restaurant_id == 16
