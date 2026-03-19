# pylint: disable=duplicate-code

import pytest
from fastapi import HTTPException
from schemas.ratings_schema import ReportCreate, ReportReason
from services.rating_service import submit_report
import services.rating_service as service_module


@pytest.mark.asyncio
async def test_report_review_spam(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 5,
        "review_text": "Buy cheap stuff at spam.com"
    }

    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: fake_order)
    monkeypatch.setattr(
        service_module, "create_report",
        lambda order_id, reason, description=None: {
            "report_id": 1,
            "order_id": order_id,
            "reason": reason,
            "description": description
        })

    payload = ReportCreate(reason=ReportReason.SPAM)
    result = submit_report("1d8e87M", payload)

    assert result["report_id"] == 1
    assert result["order_id"] == "1d8e87M"
    assert result["reason"] == ReportReason.SPAM
    assert result["message"] == "Report submitted successfully"


@pytest.mark.asyncio
async def test_report_review_inappropriate(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 1,
        "review_text": "Inappropriate content here"
    }

    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: fake_order)
    monkeypatch.setattr(
        service_module, "create_report",
        lambda order_id, reason, description=None: {
            "report_id": 2,
            "order_id": order_id,
            "reason": reason,
            "description": description
        })

    payload = ReportCreate(reason=ReportReason.INAPPROPRIATE)
    result = submit_report("1d8e87M", payload)

    assert result["reason"] == ReportReason.INAPPROPRIATE


@pytest.mark.asyncio
async def test_report_review_other_with_description(monkeypatch):
    fake_order = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 3,
        "review_text": "Some review"
    }

    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: fake_order)
    monkeypatch.setattr(
        service_module, "create_report",
        lambda order_id, reason, description=None: {
            "report_id": 3,
            "order_id": order_id,
            "reason": reason,
            "description": description
        })

    payload = ReportCreate(
        reason=ReportReason.OTHER,
        description="This review is for the wrong restaurant"
    )
    result = submit_report("1d8e87M", payload)

    assert result["reason"] == ReportReason.OTHER
    assert result["description"] == "This review is for the wrong restaurant"


@pytest.mark.asyncio
async def test_report_order_not_found(monkeypatch):
    monkeypatch.setattr(
        service_module, "get_order", lambda order_id: None)

    payload = ReportCreate(reason=ReportReason.SPAM)
    with pytest.raises(HTTPException) as exc_info:
        submit_report("FAKE_ID", payload)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_report_no_review_exists(monkeypatch):
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

    payload = ReportCreate(reason=ReportReason.SPAM)
    with pytest.raises(HTTPException) as exc_info:
        submit_report("1d8e87M", payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "No review exists to report for this order"
