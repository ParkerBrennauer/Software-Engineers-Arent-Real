# pylint: disable=duplicate-code

import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from schemas.ratings_schema import ReviewCreate
from services.rating_service import submit_review
import services.rating_service as service_module


@pytest.mark.asyncio
async def test_submit_review_success(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 5,
        "review_text": None
    }

    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: fake_order)
    monkeypatch.setattr(
        service_module, "get_restaurant_by_order", lambda order_id: 16)
    monkeypatch.setattr(
        service_module, "update_review",
        lambda order_id, review_text: {**fake_order, "review_text": review_text})

    payload = ReviewCreate(review_text="Great food, fast delivery!")
    result = submit_review("1d8e87M", payload)

    assert result["order_id"] == "1d8e87M"
    assert result["restaurant_id"] == 16
    assert result["review_text"] == "Great food, fast delivery!"


@pytest.mark.asyncio
async def test_submit_review_order_not_found(monkeypatch):
    monkeypatch.setattr(service_module, "get_order", lambda order_id: None)

    payload = ReviewCreate(review_text="Great food!")
    with pytest.raises(HTTPException) as exc_info:
        submit_review("FAKE_ORDER_ID", payload)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"


@pytest.mark.asyncio
async def test_submit_review_already_reviewed(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 5,
        "review_text": "Already wrote a review"
    }

    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: fake_order)

    payload = ReviewCreate(review_text="Trying again")
    with pytest.raises(HTTPException) as exc_info:
        submit_review("1d8e87M", payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "This order has already been reviewed"


@pytest.mark.asyncio
async def test_submit_review_restaurant_not_found(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 5,
        "review_text": None
    }

    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: fake_order)
    monkeypatch.setattr(
        service_module, "get_restaurant_by_order", lambda order_id: None)

    payload = ReviewCreate(review_text="Great food!")
    with pytest.raises(HTTPException) as exc_info:
        submit_review("1d8e87M", payload)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Restaurant not found for this order"


@pytest.mark.asyncio
async def test_review_schema_rejects_empty_text():
    with pytest.raises(ValidationError):
        ReviewCreate(review_text="")


@pytest.mark.asyncio
async def test_review_schema_accepts_valid_text():
    review = ReviewCreate(review_text="Food was amazing!")
    assert review.review_text == "Food was amazing!"
