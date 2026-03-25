import pytest
from src.repositories.user_repo import UserRepo
from src.repositories.restaurant_repo import RestaurantRepo
from src.repositories.order_repo import OrderRepo
from src.services.restaurant_owner_services import RestaurantOwnerService


@pytest.mark.asyncio
async def test_get_restaurant_orders_success_owner(monkeypatch):
    owner_data = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": 10,
        "is_active": True,
    }

    restaurants = [
        {"id": 10, "name": "Pizza Palace"},
        {"id": 11, "name": "Burger Barn"},
    ]

    orders_dict = {
        "1": {
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
        "3": {
            "id": 3,
            "items": [{"name": "Pizza", "price": 18}],
            "cost": 20.34,
            "restaurant": "Pizza Palace",
            "customer": "customer3",
            "time": 35,
            "cuisine": "Italian",
            "distance": 3.0,
            "order_status": "ready for pickup",
            "payment_status": "accepted",
        },
    }

    async def fake_get_by_username(_username: str):
        if _username == "owner1":
            return owner_data
        return None

    async def fake_read_all():
        return restaurants

    async def fake_get_all_orders():
        return orders_dict

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)
    monkeypatch.setattr(OrderRepo, "get_all_orders", fake_get_all_orders)

    orders = await RestaurantOwnerService.get_restaurant_orders(10, "owner1")

    assert len(orders) == 2
    assert orders[0].restaurant == "Pizza Palace"
    assert orders[1].restaurant == "Pizza Palace"


@pytest.mark.asyncio
async def test_get_restaurant_orders_success_staff(monkeypatch):
    staff_data = {
        "id": 2,
        "username": "staff1",
        "email": "staff@example.com",
        "name": "Staff",
        "role": "staff",
        "restaurant_id": 10,
        "is_active": True,
    }

    restaurants = [{"id": 10, "name": "Pizza Palace"}]

    orders_dict = {
        "1": {
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
    }

    async def fake_get_by_username(_username: str):
        if _username == "staff1":
            return staff_data
        return None

    async def fake_read_all():
        return restaurants

    async def fake_get_all_orders():
        return orders_dict

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)
    monkeypatch.setattr(OrderRepo, "get_all_orders", fake_get_all_orders)

    orders = await RestaurantOwnerService.get_restaurant_orders(10, "staff1")

    assert len(orders) == 1
    assert orders[0].restaurant == "Pizza Palace"


@pytest.mark.asyncio
async def test_get_restaurant_orders_permission_denied_different_restaurant(
    monkeypatch,
):
    owner_data = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": 11,
        "is_active": True,
    }

    restaurants = [
        {"id": 10, "name": "Pizza Palace"},
        {"id": 11, "name": "Burger Barn"},
    ]

    async def fake_get_by_username(_username: str):
        if _username == "owner1":
            return owner_data
        return None

    async def fake_read_all():
        return restaurants

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)

    with pytest.raises(ValueError, match="does not have permission"):
        await RestaurantOwnerService.get_restaurant_orders(10, "owner1")


@pytest.mark.asyncio
async def test_get_restaurant_orders_permission_denied_customer(monkeypatch):
    customer_data = {
        "id": 3,
        "username": "customer1",
        "email": "customer@example.com",
        "name": "Customer",
        "role": "customer",
        "is_active": True,
    }

    restaurants = [{"id": 10, "name": "Pizza Palace"}]

    async def fake_get_by_username(_username: str):
        if _username == "customer1":
            return customer_data
        return None

    async def fake_read_all():
        return restaurants

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)

    with pytest.raises(ValueError, match="does not have permission"):
        await RestaurantOwnerService.get_restaurant_orders(10, "customer1")


@pytest.mark.asyncio
async def test_get_restaurant_orders_user_not_found(monkeypatch):

    async def fake_get_by_username(_username: str):
        return None

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="User not found"):
        await RestaurantOwnerService.get_restaurant_orders(10, "nonexistent")


@pytest.mark.asyncio
async def test_get_restaurant_orders_restaurant_not_found(monkeypatch):
    owner_data = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": 999,
        "is_active": True,
    }

    restaurants = [{"id": 10, "name": "Pizza Palace"}]

    async def fake_get_by_username(_username: str):
        if _username == "owner1":
            return owner_data
        return None

    async def fake_read_all():
        return restaurants

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)

    with pytest.raises(ValueError, match="Restaurant not found"):
        await RestaurantOwnerService.get_restaurant_orders(999, "owner1")
