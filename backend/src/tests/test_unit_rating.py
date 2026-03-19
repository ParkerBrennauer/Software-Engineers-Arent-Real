import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from schemas.ratings import RatingCreate
from services.rating_service import submit_rating
import services.rating_service as rating_service_module

@pytest.mark.asyncio
async def test_submit_rating_success(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": None
    }

    updated_order = {**fake_order, "submitted_stars": 5}

    monkeypatch.setattr(rating_service_module, "get_order", lambda order_id: fake_order)
    monkeypatch.setattr(rating_service_module, "update_rating", lambda order_id, stars: updated_order)

    payload = RatingCreate(stars=5)
    result = submit_rating("1d8e87M", payload)

    assert result["order_id"] == "1d8e87M"
    assert result["stars"] == 5



@pytest.mark.asyncio
async def test_submit_rating_order_not_found(monkeypatch):
    monkeypatch.setattr(rating_service_module, "get_order", lambda order_id: None)

    payload = RatingCreate(stars=3)
    with pytest.raises(HTTPException) as exc_info:
        submit_rating("FAKE_ORDER_ID", payload)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"



@pytest.mark.asyncio
async def test_submit_rating_already_rated(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 4
    }

    monkeypatch.setattr(rating_service_module, "get_order", lambda order_id: fake_order)

    payload = RatingCreate(stars=3)
    with pytest.raises(HTTPException) as exc_info:
        submit_rating("1d8e87M", payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "This order has already been rated"



@pytest.mark.asyncio
async def test_rating_schema_rejects_zero_stars():
    with pytest.raises(ValidationError):
        RatingCreate(stars=0)


@pytest.mark.asyncio
async def test_rating_schema_rejects_six_stars():
    with pytest.raises(ValidationError):
        RatingCreate(stars=6)


@pytest.mark.asyncio
async def test_rating_schema_accepts_valid_stars():
    for star_value in range(1, 6):
        rating = RatingCreate(stars=star_value)
        assert rating.stars == star_value
