"""
Integration Tests for Feature 9 - FR1: Star-based Rating System

RUN WITH: pytest tests/test_integration_rating.py -v
(from inside the src/ directory)
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from main import app

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews.json"

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_reviews_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    yield

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(original_data, f, indent=2)


def test_rate_order_success():
    order_id = "1d8e87M"

    response = client.post(
        f"/orders/{order_id}/rating",
        json={"stars": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["stars"] == 5

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        orders = json.load(f)
    assert orders[order_id]["submitted_stars"] == 5


def test_rate_nonexistent_order():
    response = client.post(
        "/orders/NONEXISTENT_ORDER/rating",
        json={"stars": 3}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_rate_order_duplicate():
    order_id = "f4d84dC"

    response1 = client.post(
        f"/orders/{order_id}/rating",
        json={"stars": 4}
    )
    assert response1.status_code == 200

    response2 = client.post(
        f"/orders/{order_id}/rating",
        json={"stars": 2}
    )
    assert response2.status_code == 400
    assert response2.json()["detail"] == "This order has already been rated"


def test_rate_order_invalid_stars_zero():
    response = client.post(
        "/orders/1d8e87M/rating",
        json={"stars": 0}
    )
    assert response.status_code == 422


def test_rate_order_invalid_stars_six():
    response = client.post(
        "/orders/1d8e87M/rating",
        json={"stars": 6}
    )
    assert response.status_code == 422
