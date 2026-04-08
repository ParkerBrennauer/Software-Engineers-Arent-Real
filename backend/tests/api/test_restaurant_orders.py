import pytest
from fastapi import status
from src.schemas.order_schema import Order


@pytest.mark.asyncio
async def test_get_restaurant_orders_success_owner(client, monkeypatch):
    username = "owner1"
    orders = [
        {
            "id": 1,
            "items": [{"name": "Pizza", "price": 15}],
            "cost": 16.95,
            "restaurant": "Pizza Palace",
            "customer": "customer1",
            "time": 30,
            "cuisine": "Italian",
            "distance": 2.5,
            "order_status": "confirmed",
            "payment_status": "accepted",
        },
        {
            "id": 2,
            "items": [{"name": "Pizza", "price": 18}],
            "cost": 20.34,
            "restaurant": "Pizza Palace",
            "customer": "customer2",
            "time": 35,
            "cuisine": "Italian",
            "distance": 3.0,
            "order_status": "ready for pickup",
            "payment_status": "accepted",
        },
    ]

    def fake_get_current_user():
        return username

    async def fake_get_restaurant_orders(_restaurant_id: int, _username: str):
        return [Order(**order) for order in orders]

    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders",
        fake_get_restaurant_orders,
    )
    response = client.get("/restaurant_administration/restaurants/10/orders")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_restaurant_orders_success_staff(client, monkeypatch):
    username = "staff1"
    orders = [
        {
            "id": 1,
            "items": [{"name": "Pizza", "price": 15}],
            "cost": 16.95,
            "restaurant": "Pizza Palace",
            "customer": "customer1",
            "time": 30,
            "cuisine": "Italian",
            "distance": 2.5,
            "order_status": "confirmed",
            "payment_status": "accepted",
        }
    ]

    def fake_get_current_user():
        return username

    async def fake_get_restaurant_orders(_restaurant_id: int, _username: str):
        return [Order(**order) for order in orders]

    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders",
        fake_get_restaurant_orders,
    )
    response = client.get("/restaurant_administration/restaurants/10/orders")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_restaurant_orders_permission_denied(client, monkeypatch):
    username = "customer1"

    def fake_get_current_user():
        return username

    async def fake_get_restaurant_orders(_restaurant_id: int, _username: str):
        raise ValueError(
            "User does not have permission to view this restaurant's orders"
        )

    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders",
        fake_get_restaurant_orders,
    )
    response = client.get("/restaurant_administration/restaurants/10/orders")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "does not have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_restaurant_orders_user_not_found(client, monkeypatch):
    username = "nonexistent"

    def fake_get_current_user():
        return username

    async def fake_get_restaurant_orders(_restaurant_id: int, _username: str):
        raise ValueError("User not found")

    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders",
        fake_get_restaurant_orders,
    )
    response = client.get("/restaurant_administration/restaurants/10/orders")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_restaurant_orders_restaurant_not_found(client, monkeypatch):
    username = "owner1"

    def fake_get_current_user():
        return username

    async def fake_get_restaurant_orders(_restaurant_id: int, _username: str):
        raise ValueError("Restaurant not found")

    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders",
        fake_get_restaurant_orders,
    )
    response = client.get("/restaurant_administration/restaurants/999/orders")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Restaurant not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_restaurant_orders_missing_username(client):
    def fake_get_current_user():
        return None

    import unittest.mock

    with unittest.mock.patch(
        "src.api.routers.restaurant_administration_router.UserService.get_current_user",
        return_value=None,
    ):
        response = client.get("/restaurant_administration/restaurants/10/orders")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No user currently logged in" in response.json()["detail"]
