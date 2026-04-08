import pytest
from src.repositories.user_repo import UserRepo
from src.repositories.restaurant_repo import RestaurantRepo
from src.repositories.order_repo import OrderRepo
from src.services.restaurant_owner_services import RestaurantOwnerService
from src.schemas.order_schema import OrderStatus

async def _mock_get_by_username(_):
    return {'username': 'owner1', 'role': 'owner', 'restaurant_id': 10}

async def _mock_read_all():
    return [{'id': 10, 'name': 'Pizza'}]

async def _mock_get_orders(*args, **kwargs):
    return [{'id': 1, 'items': ['Pizza'], 'cost': 16.95, 'restaurant': 'Pizza', 'customer': 'c1', 'time': 150, 'cuisine': 'Italian', 'distance': 2.5, 'order_status': OrderStatus.CONFIRMED.value, 'payment_status': 'accepted'}]

@pytest.mark.asyncio
async def test_filter_by_status_owner(monkeypatch):
    monkeypatch.setattr(UserRepo, 'get_by_username', _mock_get_by_username)
    monkeypatch.setattr(RestaurantRepo, 'read_all', _mock_read_all)
    monkeypatch.setattr(OrderRepo, 'get_orders_by_status', _mock_get_orders)
    result = await RestaurantOwnerService.get_restaurant_orders_by_status(10, 'owner1', OrderStatus.CONFIRMED.value)
    assert len(result) == 1 and result[0].restaurant == 'Pizza'

@pytest.mark.asyncio
async def test_filter_by_status_denied(monkeypatch):
    monkeypatch.setattr(UserRepo, 'get_by_username', _mock_get_by_username)
    with pytest.raises(ValueError, match='does not have permission'):
        await RestaurantOwnerService.get_restaurant_orders_by_status(20, 'owner1', OrderStatus.CONFIRMED.value)

@pytest.mark.asyncio
async def test_filter_by_date_range(monkeypatch):
    monkeypatch.setattr(UserRepo, 'get_by_username', _mock_get_by_username)
    monkeypatch.setattr(RestaurantRepo, 'read_all', _mock_read_all)
    monkeypatch.setattr(OrderRepo, 'get_orders_by_date_range', _mock_get_orders)
    result = await RestaurantOwnerService.get_restaurant_orders_by_date_range(10, 'owner1', 100, 200)
    assert len(result) == 1

@pytest.mark.asyncio
async def test_filter_by_status_and_date(monkeypatch):
    monkeypatch.setattr(UserRepo, 'get_by_username', _mock_get_by_username)
    monkeypatch.setattr(RestaurantRepo, 'read_all', _mock_read_all)
    monkeypatch.setattr(OrderRepo, 'get_orders_by_status_and_date', _mock_get_orders)
    result = await RestaurantOwnerService.get_restaurant_orders_by_status_and_date(10, 'owner1', OrderStatus.CONFIRMED.value, 100, 200)
    assert len(result) == 1

@pytest.mark.asyncio
async def test_filter_by_status_staff_access(monkeypatch):

    async def mock_staff(_):
        return {'username': 'staff1', 'role': 'staff', 'restaurant_id': 10}
    monkeypatch.setattr(UserRepo, 'get_by_username', mock_staff)
    monkeypatch.setattr(RestaurantRepo, 'read_all', _mock_read_all)
    monkeypatch.setattr(OrderRepo, 'get_orders_by_status', _mock_get_orders)
    result = await RestaurantOwnerService.get_restaurant_orders_by_status(10, 'staff1', OrderStatus.CONFIRMED.value)
    assert len(result) == 1

@pytest.mark.asyncio
async def test_filter_user_not_found(monkeypatch):

    async def mock_none(_):
        return None
    monkeypatch.setattr(UserRepo, 'get_by_username', mock_none)
    with pytest.raises(ValueError, match='User not found'):
        await RestaurantOwnerService.get_restaurant_orders_by_status(10, 'unknown', OrderStatus.CONFIRMED.value)

@pytest.mark.asyncio
async def test_filter_restaurant_not_found(monkeypatch):
    monkeypatch.setattr(UserRepo, 'get_by_username', _mock_get_by_username)

    async def mock_other_restaurant():
        return [{'id': 20, 'name': 'Other'}]
    monkeypatch.setattr(RestaurantRepo, 'read_all', mock_other_restaurant)
    with pytest.raises(ValueError, match='Restaurant not found'):
        await RestaurantOwnerService.get_restaurant_orders_by_status(10, 'owner1', OrderStatus.CONFIRMED.value)
