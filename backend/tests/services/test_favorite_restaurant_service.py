import pytest
from src.repositories.customer_repo import CustomerRepo
from src.repositories.restaurant_repo import RestaurantRepo
from src.services.favorite_restaurant_service import FavoriteRestaurantService

@pytest.mark.asyncio
async def test_get_favorite_restaurants_defaults_to_empty_list(monkeypatch):

    async def fake_get_by_id(_customer_id: str):
        return {'order_ids': ['1d8e87M']}
    monkeypatch.setattr(CustomerRepo, 'get_by_id', fake_get_by_id)
    result = await FavoriteRestaurantService.get_favorite_restaurants('customer-1')
    assert result.customer_id == 'customer-1'
    assert result.favorite_restaurants == []

@pytest.mark.asyncio
async def test_add_favorite_restaurant_success(monkeypatch):
    customer = {'favorite_restaurants': [16]}
    captured = {}

    async def fake_get_by_id(_customer_id: str):
        return dict(customer)

    async def fake_read_all():
        return [{'restaurant_id': 16}, {'restaurant_id': 30}]

    async def fake_update_by_id(customer_id: str, updates: dict):
        captured['customer_id'] = customer_id
        captured['updates'] = updates
        return {**customer, **updates}
    monkeypatch.setattr(CustomerRepo, 'get_by_id', fake_get_by_id)
    monkeypatch.setattr(RestaurantRepo, 'read_all', fake_read_all)
    monkeypatch.setattr(CustomerRepo, 'update_by_id', fake_update_by_id)
    result = await FavoriteRestaurantService.add_favorite_restaurant('customer-1', 30)
    assert result.customer_id == 'customer-1'
    assert result.restaurant_id == 30
    assert result.favorite_restaurants == [16, 30]
    assert captured == {'customer_id': 'customer-1', 'updates': {'favorite_restaurants': [16, 30]}}

@pytest.mark.asyncio
async def test_add_favorite_restaurant_rejects_duplicate(monkeypatch):

    async def fake_get_by_id(_customer_id: str):
        return {'favorite_restaurants': [16]}

    async def fake_read_all():
        return [{'restaurant_id': 16}]
    monkeypatch.setattr(CustomerRepo, 'get_by_id', fake_get_by_id)
    monkeypatch.setattr(RestaurantRepo, 'read_all', fake_read_all)
    with pytest.raises(ValueError, match='Restaurant is already in favorites'):
        await FavoriteRestaurantService.add_favorite_restaurant('customer-1', 16)

@pytest.mark.asyncio
async def test_remove_favorite_restaurant_success(monkeypatch):
    customer = {'favorite_restaurants': [16, 30]}

    async def fake_get_by_id(_customer_id: str):
        return dict(customer)

    async def fake_update_by_id(_customer_id: str, updates: dict):
        return {**customer, **updates}
    monkeypatch.setattr(CustomerRepo, 'get_by_id', fake_get_by_id)
    monkeypatch.setattr(CustomerRepo, 'update_by_id', fake_update_by_id)
    result = await FavoriteRestaurantService.remove_favorite_restaurant('customer-1', 16)
    assert result.restaurant_id == 16
    assert result.favorite_restaurants == [30]
    assert result.message == 'Restaurant removed from favorites'

@pytest.mark.asyncio
async def test_add_favorite_restaurant_rejects_missing_customer(monkeypatch):

    async def fake_get_by_id(_customer_id: str):
        return None
    monkeypatch.setattr(CustomerRepo, 'get_by_id', fake_get_by_id)
    with pytest.raises(ValueError, match='Customer not found'):
        await FavoriteRestaurantService.add_favorite_restaurant('customer-404', 16)
