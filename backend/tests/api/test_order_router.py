import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app

client = TestClient(app, raise_server_exceptions=False)


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.repositories.order_repo.OrderRepo.get_by_id", new_callable=AsyncMock)
@patch(
    "src.services.order_services.OrderService.get_order_status", new_callable=AsyncMock
)
async def test_get_order_status_success(
    mock_service, mock_get_by_id, mock_current_user
):
    mock_current_user.return_value = "customer1"
    mock_get_by_id.return_value = {"id": "1", "customer": "customer1"}
    mock_service.return_value = {"order_id": "1", "status": "processing"}
    response = client.get("/orders/1")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.repositories.order_repo.OrderRepo.get_by_id", new_callable=AsyncMock)
async def test_get_order_status_not_found(mock_get_by_id, mock_current_user):
    mock_current_user.return_value = "customer1"
    mock_get_by_id.return_value = None
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
@patch(
    "src.services.order_services.OrderService.get_restaurant_orders",
    new_callable=AsyncMock,
)
async def test_get_restaurant_orders_success(mock_service):
    mock_service.return_value = [{"order_id": "1"}]
    response = client.get("/orders/restaurant/mcdonalds")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
@patch(
    "src.services.order_services.OrderService.get_restaurant_orders",
    new_callable=AsyncMock,
)
async def test_get_restaurant_orders_empty(mock_service):
    mock_service.return_value = []
    response = client.get("/orders/restaurant/unknown")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.repositories.order_repo.OrderRepo.get_by_id", new_callable=AsyncMock)
@patch("src.services.order_services.OrderService.cancel_order", new_callable=AsyncMock)
async def test_cancel_order_success(mock_service, mock_get_by_id, mock_current_user):
    mock_current_user.return_value = "customer1"
    mock_get_by_id.return_value = {"id": "1", "customer": "customer1"}
    mock_service.return_value = {"status": "cancelled"}
    response = client.put("/orders/1/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


@pytest.mark.asyncio
@patch(
    "src.services.order_services.OrderService.mark_ready_for_pickup",
    new_callable=AsyncMock,
)
async def test_mark_ready_success(mock_service):
    mock_service.return_value = {"status": "ready"}
    response = client.put("/orders/1/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.asyncio
@patch(
    "src.services.order_services.OrderService.report_restaurant_delay",
    new_callable=AsyncMock,
)
async def test_restaurant_delay_success(mock_service):
    mock_service.return_value = {"status": "delayed"}
    response = client.put("/orders/1/restaurant-delay?reason=busy")
    assert response.status_code == 200
    assert response.json()["status"] == "delayed"


@pytest.mark.asyncio
async def test_restaurant_delay_missing_reason():
    response = client.put("/orders/1/restaurant-delay")
    assert response.status_code == 422


@pytest.mark.asyncio
@patch(
    "src.services.order_services.OrderService.get_driver_orders", new_callable=AsyncMock
)
async def test_get_driver_orders_success(mock_service):
    mock_service.return_value = [{"order_id": "1"}]
    response = client.get("/orders/driver/john")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
@patch("src.services.order_services.OrderService.pickup_order", new_callable=AsyncMock)
async def test_pickup_order_success(mock_service):
    mock_service.return_value = {"status": "picked_up"}
    response = client.put("/orders/1/pickup")
    assert response.status_code == 200
    assert response.json()["status"] == "picked_up"


@pytest.mark.asyncio
@patch(
    "src.services.order_services.OrderService.report_driver_delay",
    new_callable=AsyncMock,
)
async def test_driver_delay_success(mock_service):
    mock_service.return_value = {"status": "delayed"}
    response = client.put("/orders/1/driver-delay?reason=traffic")
    assert response.status_code == 200
    assert response.json()["status"] == "delayed"


@pytest.mark.asyncio
async def test_driver_delay_missing_reason():
    response = client.put("/orders/1/driver-delay")
    assert response.status_code == 422


@pytest.mark.asyncio
@patch("src.services.order_services.OrderService.assign_driver", new_callable=AsyncMock)
async def test_assign_driver_success(mock_service):
    mock_service.return_value = {"driver": "john"}
    response = client.put("/orders/1/assign-driver?driver=john")
    assert response.status_code == 200
    assert response.json()["driver"] == "john"


@pytest.mark.asyncio
async def test_assign_driver_missing_driver():
    response = client.put("/orders/1/assign-driver")
    assert response.status_code == 422


@pytest.mark.asyncio
@patch(
    "src.services.order_services.OrderService.process_refund", new_callable=AsyncMock
)
async def test_refund_order_success(mock_service):
    mock_service.return_value = {"status": "refunded"}
    response = client.put("/orders/1/refund")
    assert response.status_code == 200
    assert response.json()["status"] == "refunded"


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.services.order_services.OrderService.create_order", new_callable=AsyncMock)
async def test_submit_order_success(mock_service, mock_current_user):
    mock_current_user.return_value = "john_doe"
    mock_service.return_value = {
        "id": 1,
        "order_status": "payment pending",
        "payment_status": "pending",
        "items": [{"name": "Burger", "price": 10.99}],
        "cost": 12.42,
        "locked": False,
    }
    order_data = {
        "items": [{"name": "Burger", "price": 10.99}],
        "restaurant": "mcdonalds",
        "customer": "wrong_customer",
        "time": 30,
        "cuisine": "fast_food",
        "distance": 2.5,
    }
    response = client.post("/orders/place", json=order_data)
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["order_status"] == "payment pending"
    assert response.json()["payment_status"] == "pending"


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.services.order_services.OrderService.pay_order", new_callable=AsyncMock)
async def test_pay_order_success(mock_pay, mock_current_user):
    mock_current_user.return_value = "john_doe"
    mock_pay.return_value = {
        "items": [],
        "cost": 12.0,
        "restaurant": "Restaurant_1",
        "customer": "john_doe",
        "time": 25,
        "cuisine": "Italian",
        "distance": 2.0,
        "order_status": "confirmed",
        "payment_status": "accepted",
        "id": 5,
    }
    response = client.post("/orders/5/pay", json={"simulate": "accept"})
    assert response.status_code == 200
    assert response.json()["payment_status"] == "accepted"
    mock_pay.assert_called_once()
    assert mock_pay.call_args[0][0] == "5"
    assert mock_pay.call_args[0][1] == "john_doe"


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.services.order_services.OrderService.create_order", new_callable=AsyncMock)
async def test_submit_order_error(mock_service, mock_current_user):
    mock_current_user.return_value = "john_doe"
    mock_service.side_effect = ValueError("Invalid restaurant")
    order_data = {
        "items": [{"name": "Burger", "price": 10.99}],
        "restaurant": "unknown",
        "customer": "john_doe",
        "time": 30,
        "cuisine": "fast_food",
        "distance": 2.5,
    }
    response = client.post("/orders/place", json=order_data)
    assert response.status_code == 400
    assert "Invalid restaurant" in response.json()["detail"]


@pytest.mark.asyncio
async def test_submit_order_missing_required_field():
    order_data = {
        "items": [{"name": "Burger", "price": 10.99}],
        "restaurant": "mcdonalds",
        "time": 30,
        "cuisine": "fast_food",
        "distance": 2.5,
    }
    response = client.post("/orders/place", json=order_data)
    assert response.status_code == 422


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.repositories.order_repo.OrderRepo.get_by_id", new_callable=AsyncMock)
@patch("src.services.order_services.OrderService.update_order", new_callable=AsyncMock)
async def test_add_items_to_order_success(
    mock_service, mock_get_by_id, mock_current_user
):
    mock_current_user.return_value = "customer1"
    mock_get_by_id.return_value = {"id": "1", "customer": "customer1"}
    mock_service.return_value = {
        "id": 1,
        "order_status": "payment pending",
        "payment_status": "pending",
        "items": [{"name": "Burger", "price": 10.99}, {"name": "Fries", "price": 4.99}],
        "cost": 18.62,
        "locked": False,
    }
    items_data = {
        "items": [{"name": "Burger", "price": 10.99}, {"name": "Fries", "price": 4.99}]
    }
    response = client.post("/orders/1/items", json=items_data)
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
    assert response.json()["cost"] == 18.62


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.repositories.order_repo.OrderRepo.get_by_id", new_callable=AsyncMock)
@patch("src.services.order_services.OrderService.update_order", new_callable=AsyncMock)
async def test_add_items_to_order_locked_error(
    mock_service, mock_get_by_id, mock_current_user
):
    mock_current_user.return_value = "customer1"
    mock_get_by_id.return_value = {"id": "1", "customer": "customer1"}
    mock_service.side_effect = ValueError("Order is locked and cannot be updated")
    items_data = {"items": [{"name": "Burger", "price": 10.99}]}
    response = client.post("/orders/1/items", json=items_data)
    assert response.status_code == 400
    assert "Order is locked" in response.json()["detail"]


@pytest.mark.asyncio
@patch("src.services.user_service.UserService.get_current_user")
@patch("src.repositories.order_repo.OrderRepo.get_by_id", new_callable=AsyncMock)
@patch("src.services.order_services.OrderService.update_order", new_callable=AsyncMock)
async def test_add_items_to_order_empty_items(
    mock_service, mock_get_by_id, mock_current_user
):
    mock_current_user.return_value = "customer1"
    mock_get_by_id.return_value = {"id": "1", "customer": "customer1"}
    mock_service.return_value = {
        "id": 1,
        "order_status": "payment pending",
        "payment_status": "pending",
        "items": [],
        "cost": 0.0,
        "locked": False,
    }
    items_data = {"items": []}
    response = client.post("/orders/1/items", json=items_data)
    assert response.status_code == 200
    assert response.json()["items"] == []
