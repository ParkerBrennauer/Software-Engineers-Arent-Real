# pylint: disable=duplicate-code

import pytest
from fastapi import HTTPException
from services.rating_service import check_feedback_prompt
import services.rating_service as service_module


@pytest.mark.asyncio
async def test_feedback_prompt_success(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": None,
        "review_text": None
    }

    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: fake_order)

    result = check_feedback_prompt("1d8e87M")

    assert result["order_id"] == "1d8e87M"
    assert result["prompt_feedback"] is True
    assert "rating and review" in result["message"]


@pytest.mark.asyncio
async def test_feedback_prompt_order_not_found(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: None)

    with pytest.raises(HTTPException) as exc_info:
        check_feedback_prompt("FAKE_ID")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"
