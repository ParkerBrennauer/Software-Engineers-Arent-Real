from urllib import response

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.api.routers.order_router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

def test_get_order_status():
    mock_data = {"id": 1, "order_status": "out for delivery"}

    with patch(
        "src.api.routers.order_router.OrderService.get_order_status",
        new=AsyncMock(return_value=mock_data),
    ):
        response = client.get("/orders/1")

    assert response.status_code == 200
    assert response.json() == mock_data


def test_cancel_order():
    mock_data = {"id": 1, "order_status": "cancelled"}

    with patch(
        "src.api.routers.order_router.OrderService.cancel_order",
        new=AsyncMock(return_value=mock_data),
    ):
        response = client.put("/orders/1/cancel")

    assert response.status_code == 200
    assert response.json()["order_status"] == "cancelled"


def test_assign_driver():
    mock_data = {"id": 1, "driver": "Alice"}

    with patch(
        "src.api.routers.order_router.OrderService.assign_driver",
        new=AsyncMock(return_value=mock_data),
    ):
        response = client.put("/orders/1/assign-driver?driver=Alice")

    assert response.status_code == 200
    assert response.json()["driver"] == "Alice"


def test_get_driver_orders():
    mock_data = [{"id": 1, "driver": "Bob"}]

    with patch(
        "src.api.routers.order_router.OrderService.get_driver_orders",
        new=AsyncMock(return_value=mock_data),
    ):
        response = client.get("/orders/driver/Bob")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_order_tracking():
    mock_data = {
        "order_id": "1",
        "restaurant": "Test Restaurant",
        "customer": "JohnDoe",
        "order_status": "out for delivery",
        "current_location": "Downtown",
        "distance_km": 2.5,
        "estimated_time_minutes": 10,
        "status_message": "On the way",
    }

    with patch(
        "src.api.routers.order_router.OrderTrackingService.get_tracking_info",
        new=AsyncMock(return_value=mock_data),
    ):
        response = client.get("/orders/1/tracking")

    assert response.status_code == 200
    assert response.json()["order_status"] == "out for delivery"


def test_get_order_tracking_not_found():
    with patch(
        "src.api.routers.order_router.OrderTrackingService.get_tracking_info",
            new=AsyncMock(side_effect=ValueError("Order not found")),
    ):
        response = client.get("/orders/999/tracking")


    assert response.status_code in [404, 500]
