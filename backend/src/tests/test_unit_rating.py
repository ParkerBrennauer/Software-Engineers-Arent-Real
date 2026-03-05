"""
Unit Tests for Feature 9 - FR1: Star-based Rating System

RUN WITH: pytest tests/test_unit_rating.py -v
(from inside the src/ directory)
"""

from unittest.mock import patch

import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from schemas.ratings import RatingCreate  # pylint: disable=import-error
from services.rating_service import submit_rating  # pylint: disable=import-error


# ---------------------------------------------------------------------------
# Unit Test 1: submit_rating succeeds for a valid, unrated order
# ---------------------------------------------------------------------------

@patch("services.rating_service.update_rating")
@patch("services.rating_service.get_order")
def test_submit_rating_success(mock_get_order, mock_update_rating):
    # set up our fake data
    mock_get_order.return_value = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": None
    }
    mock_update_rating.return_value = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 5
    }

    # call the function we're testing
    payload = RatingCreate(stars=5)
    result = submit_rating("1d8e87M", payload)

    # check the output is what we expect
    assert result["order_id"] == "1d8e87M"
    assert result["stars"] == 5

    mock_get_order.assert_called_once_with("1d8e87M")
    mock_update_rating.assert_called_once_with("1d8e87M", 5)


# ---------------------------------------------------------------------------
# Unit Test 2: submit_rating raises 404 for a nonexistent order
# ---------------------------------------------------------------------------

@patch("services.rating_service.get_order")
def test_submit_rating_order_not_found(mock_get_order):
    # get_order returns None (order doesn't exist)
    mock_get_order.return_value = None

    # should raise HTTPException with 404
    payload = RatingCreate(stars=3)
    with pytest.raises(HTTPException) as exc_info:
        submit_rating("FAKE_ORDER_ID", payload)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"


# ---------------------------------------------------------------------------
# Unit Test 3: submit_rating raises 400 for an already-rated order
# ---------------------------------------------------------------------------

@patch("services.rating_service.get_order")
def test_submit_rating_already_rated(mock_get_order):
    # order already has a rating
    mock_get_order.return_value = {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": 4
    }

    # should raise HTTPException with 400
    payload = RatingCreate(stars=3)
    with pytest.raises(HTTPException) as exc_info:
        submit_rating("1d8e87M", payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "This order has already been rated"


# ---------------------------------------------------------------------------
# Unit Test 4: RatingCreate schema validates star range (1-5)
# ---------------------------------------------------------------------------

def test_rating_schema_rejects_zero_stars():
    with pytest.raises(ValidationError):
        RatingCreate(stars=0)


def test_rating_schema_rejects_six_stars():
    with pytest.raises(ValidationError):
        RatingCreate(stars=6)


def test_rating_schema_accepts_valid_stars():
    # All values 1 through 5 should work
    for star_value in range(1, 6):
        rating = RatingCreate(stars=star_value)
        assert rating.stars == star_value
