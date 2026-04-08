import pytest
from src.services.restaurant_services import RestaurantService
from src.repositories.restaurant_repo import RestaurantRepo
from src.schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate
from src.services.item_services import ItemService
from src.schemas.item_schema import ItemCreate

@pytest.mark.asyncio
async def test_get_restaurant_menu_and_not_found(monkeypatch):
    restaurants_data = [{'restaurant_id': 10, 'cuisine': 'Indian'}]

    async def fake_read_all():
        return restaurants_data

    async def fake_get_items_by_restaurant_id(_restaurant_id: int):
        raise AssertionError("Should not call ItemService if restaurant doesn't exist")
    monkeypatch.setattr(RestaurantRepo, 'read_all', fake_read_all)
    monkeypatch.setattr(ItemService, 'get_items_by_restaurant_id', fake_get_items_by_restaurant_id)
    with pytest.raises(ValueError) as excinfo:
        await RestaurantService.get_restaurant_menu(999)
    assert str(excinfo.value) == 'Restaurant not found'

@pytest.mark.asyncio
async def test_update_restaurant_raises_when_not_found(monkeypatch):
    existing_restaurants = [{'id': 1, 'restaurant_id': 1, 'cuisine': 'Italian', 'ratings': {'taste': 4}, 'orders': [], 'menu': []}, {'id': 2, 'restaurant_id': 2, 'cuisine': 'Japanese', 'ratings': {'taste': 5}, 'orders': [], 'menu': []}]

    async def fake_read_all():
        return [r.copy() for r in existing_restaurants]

    async def fake_write_restaurant(_data):
        pytest.fail('write_restaurant should not be called when restaurant is not found')
    monkeypatch.setattr(RestaurantRepo, 'read_all', fake_read_all)
    monkeypatch.setattr(RestaurantRepo, 'write_restaurant', fake_write_restaurant)
    restaurant_update = RestaurantUpdate(cuisine='Thai', menu=[ItemCreate(item_name='Pad Thai', restaurant_id=999, cost=16.5, cuisine='Thai')])
    with pytest.raises(ValueError, match='Restaurant not found'):
        await RestaurantService.update_restaurant(999, restaurant_update)
