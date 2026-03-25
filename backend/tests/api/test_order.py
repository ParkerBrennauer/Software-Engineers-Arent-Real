import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app


client = TestClient(app)



@patch("src.services.order_services.OrderService.get_order_status", new_callable=AsyncMock)
def test_get_order_status_success(mock_service):
    mock_service.return_value = {"order_id": "1", "status": "processing"}

    response = client.get("/orders/1")

    assert response.status_code == 200
    assert response.json()["status"] == "processing"

@patch("src.services.order_services.OrderService.get_order_status", new_callable=AsyncMock)
def test_get_order_status_not_found(mock_service):
    mock_service.return_value = None

    response = client.get("/orders/999")

    assert response.status_code == 200
    assert response.json() is None

@patch("src.services.order_services.OrderService.get_restaurant_orders", new_callable=AsyncMock)
def test_get_restaurant_orders_success(mock_service):
    mock_service.return_value = [{"order_id": "1"}]

    response = client.get("/orders/restaurant/mcdonalds")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("src.services.order_services.OrderService.get_restaurant_orders", new_callable=AsyncMock)
def test_get_restaurant_orders_empty(mock_service):
    mock_service.return_value = []

    response = client.get("/orders/restaurant/unknown")

    assert response.status_code == 200
    assert response.json() == []

@patch("src.services.order_services.OrderService.cancel_order", new_callable=AsyncMock)
def test_cancel_order_success(mock_service):
    mock_service.return_value = {"status": "cancelled"}

    response = client.put("/orders/1/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"