# pylint: disable=duplicate-code

import pytest
from fastapi import HTTPException
from services.rating_service import get_filtered_reviews
import services.rating_service as service_module


@pytest.mark.asyncio
async def test_filter_reviews_no_filter(monkeypatch):
    fake_reviews = [
        {"order_id": "abc123", "submitted_stars": 5, "review_text": "Amazing!"},
        {"order_id": "def456", "submitted_stars": 3, "review_text": "Okay"},
        {"order_id": "ghi789", "submitted_stars": 1, "review_text": "Bad"},
    ]

    monkeypatch.setattr(
        service_module, "get_restaurant_reviews",
        lambda restaurant_id, stars=None: fake_reviews)

    result = get_filtered_reviews(16)

    assert result["restaurant_id"] == 16
    assert result["stars_filter"] is None
    assert result["total_reviews"] == 3
    assert len(result["reviews"]) == 3


@pytest.mark.asyncio
async def test_filter_reviews_by_stars(monkeypatch):
    fake_reviews = [
        {"order_id": "abc123", "submitted_stars": 5, "review_text": "Amazing!"},
    ]

    monkeypatch.setattr(
        service_module, "get_restaurant_reviews",
        lambda restaurant_id, stars=None: fake_reviews)

    result = get_filtered_reviews(16, stars=5)

    assert result["stars_filter"] == 5
    assert result["total_reviews"] == 1
    assert result["reviews"][0]["submitted_stars"] == 5


@pytest.mark.asyncio
async def test_filter_reviews_empty_result(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_restaurant_reviews",
        lambda restaurant_id, stars=None: [])

    result = get_filtered_reviews(16, stars=2)

    assert result["total_reviews"] == 0
    assert result["reviews"] == []


@pytest.mark.asyncio
async def test_filter_reviews_restaurant_not_found(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_restaurant_reviews",
        lambda restaurant_id, stars=None: None)

    with pytest.raises(HTTPException) as exc_info:
        get_filtered_reviews(9999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Restaurant not found"
