# pylint: disable=duplicate-code

import pytest
from fastapi import HTTPException
from schemas.ratings_schema import ReviewEdit
from services.rating_service import edit_order_review, delete_order_review
import services.rating_service as service_module


FAKE_ORDER_WITH_REVIEW = {
    "customer_rating": 4,
    "food_temperature": "Hot",
    "food_freshness": 5,
    "packaging_quality": 1,
    "food_condition": "Fair",
    "customer_satisfaction": 3,
    "submitted_stars": 4,
    "review_text": "Pretty good food"
}

FAKE_ORDER_NO_REVIEW = {
    "customer_rating": 4,
    "food_temperature": "Hot",
    "food_freshness": 5,
    "packaging_quality": 1,
    "food_condition": "Fair",
    "customer_satisfaction": 3,
    "submitted_stars": None,
    "review_text": None
}


# --- Edit Tests ---

@pytest.mark.asyncio
async def test_edit_review_update_both(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order",
        lambda order_id: {**FAKE_ORDER_WITH_REVIEW})
    monkeypatch.setattr(
        service_module, "edit_review",
        lambda order_id, stars=None, review_text=None: {
            **FAKE_ORDER_WITH_REVIEW,
            "submitted_stars": stars or FAKE_ORDER_WITH_REVIEW["submitted_stars"],
            "review_text": review_text or FAKE_ORDER_WITH_REVIEW["review_text"]
        })

    payload = ReviewEdit(stars=5, review_text="Updated review")
    result = edit_order_review("1d8e87M", payload)

    assert result["order_id"] == "1d8e87M"
    assert result["submitted_stars"] == 5
    assert result["review_text"] == "Updated review"


@pytest.mark.asyncio
async def test_edit_review_update_stars_only(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order",
        lambda order_id: {**FAKE_ORDER_WITH_REVIEW})
    monkeypatch.setattr(
        service_module, "edit_review",
        lambda order_id, stars=None, review_text=None: {
            **FAKE_ORDER_WITH_REVIEW, "submitted_stars": stars
        })

    payload = ReviewEdit(stars=2)
    result = edit_order_review("1d8e87M", payload)

    assert result["submitted_stars"] == 2


@pytest.mark.asyncio
async def test_edit_review_order_not_found(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: None)

    payload = ReviewEdit(stars=3)
    with pytest.raises(HTTPException) as exc_info:
        edit_order_review("FAKE_ID", payload)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_edit_review_no_existing_review(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order",
        lambda order_id: {**FAKE_ORDER_NO_REVIEW})

    payload = ReviewEdit(stars=3)
    with pytest.raises(HTTPException) as exc_info:
        edit_order_review("1d8e87M", payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "No review exists to edit for this order"


@pytest.mark.asyncio
async def test_edit_review_nothing_to_update(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order",
        lambda order_id: {**FAKE_ORDER_WITH_REVIEW})

    payload = ReviewEdit()
    with pytest.raises(HTTPException) as exc_info:
        edit_order_review("1d8e87M", payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Nothing to update"


# --- Delete Tests ---

@pytest.mark.asyncio
async def test_delete_review_success(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order",
        lambda order_id: {**FAKE_ORDER_WITH_REVIEW})
    monkeypatch.setattr(
        service_module, "delete_review",
        lambda order_id: {**FAKE_ORDER_NO_REVIEW})

    result = delete_order_review("1d8e87M")

    assert result["order_id"] == "1d8e87M"
    assert result["message"] == "Review and rating deleted successfully"


@pytest.mark.asyncio
async def test_delete_review_order_not_found(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: None)

    with pytest.raises(HTTPException) as exc_info:
        delete_order_review("FAKE_ID")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_review_nothing_to_delete(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order",
        lambda order_id: {**FAKE_ORDER_NO_REVIEW})

    with pytest.raises(HTTPException) as exc_info:
        delete_order_review("1d8e87M")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "No review exists to delete for this order"