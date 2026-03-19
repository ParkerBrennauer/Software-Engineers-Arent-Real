# pylint: disable=redefined-outer-name,unused-argument,duplicate-code

import pytest
from httpx import ASGITransport, AsyncClient
from main import app
import services.rating_service as service_module

@pytest.fixture
def async_client():

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


FAKE_ORDERS = {
    "1d8e87M": {
        "customer_rating": 4,
        "food_temperature": "Hot",
        "food_freshness": 5,
        "packaging_quality": 1,
        "food_condition": "Fair",
        "customer_satisfaction": 3,
        "submitted_stars": None
    },
    "f4d84dC": {
        "customer_rating": 1,
        "food_temperature": "Warm",
        "food_freshness": 3,
        "packaging_quality": 2,
        "food_condition": "Fair",
        "customer_satisfaction": 5,
        "submitted_stars": None
    }
}



@pytest.mark.asyncio
async def test_rate_order_success(async_client, monkeypatch):
    order_data = {**FAKE_ORDERS["1d8e87M"]}

    def fake_get_order(order_id):
        if order_id == "1d8e87M":
            return order_data
        return None

    def fake_update_rating(order_id, stars):
        order_data["submitted_stars"] = stars
        return order_data

    monkeypatch.setattr(service_module, "get_order", fake_get_order)
    monkeypatch.setattr(service_module, "update_rating", fake_update_rating)

    response = await async_client.post(
        "/orders/1d8e87M/rating",
        json={"stars": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "1d8e87M"
    assert data["stars"] == 5


@pytest.mark.asyncio
async def test_rate_nonexistent_order(async_client, monkeypatch):
    monkeypatch.setattr(service_module, "get_order", lambda order_id: None)

    response = await async_client.post(
        "/orders/NONEXISTENT_ORDER/rating",
        json={"stars": 3}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"



@pytest.mark.asyncio
async def test_rate_order_duplicate(async_client, monkeypatch):
    order_data = {**FAKE_ORDERS["f4d84dC"]}

    def fake_get_order(order_id):
        return order_data

    def fake_update_rating(order_id, stars):
        order_data["submitted_stars"] = stars
        return order_data

    monkeypatch.setattr(service_module, "get_order", fake_get_order)
    monkeypatch.setattr(service_module, "update_rating", fake_update_rating)

    response1 = await async_client.post(
        "/orders/f4d84dC/rating",
        json={"stars": 4}
    )
    assert response1.status_code == 200

    response2 = await async_client.post(
        "/orders/f4d84dC/rating",
        json={"stars": 2}
    )
    assert response2.status_code == 400
    assert response2.json()["detail"] == "This order has already been rated"


@pytest.mark.asyncio
async def test_rate_order_invalid_stars_zero(async_client, monkeypatch):
    monkeypatch.setattr(service_module, "get_order", lambda order_id: FAKE_ORDERS["1d8e87M"])

    response = await async_client.post(
        "/orders/1d8e87M/rating",
        json={"stars": 0}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rate_order_invalid_stars_six(async_client, monkeypatch):
    monkeypatch.setattr(service_module, "get_order", lambda order_id: FAKE_ORDERS["1d8e87M"])

    response = await async_client.post(
        "/orders/1d8e87M/rating",
        json={"stars": 6}
    )
    assert response.status_code == 422
