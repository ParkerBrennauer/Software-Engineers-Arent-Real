from fastapi.testclient import TestClient
from src.main import app
from src.services.item_services import ItemService
client = TestClient(app)

def test_get_item_by_key_success(monkeypatch):

    async def fake_get_items_by_key(_item_key: str):
        return {'item_name': 'Pad Thai', 'restaurant_id': 2, 'cost': 16.5, 'cuisine': 'Thai', 'times_ordered': 12, 'avg_rating': 4.7, 'dietary': {'vegan': False, 'vegetarian': False, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}}
    monkeypatch.setattr(ItemService, 'get_items_by_key', fake_get_items_by_key)
    response = client.get('/items/Pad Thai')
    assert response.status_code == 200
    data = response.json()
    assert data['item_name'] == 'Pad Thai'
    assert data['restaurant_id'] == 2

def test_get_item_by_key_returns_not_found(monkeypatch):

    async def fake_get_items_by_key(_item_key: str):
        return None
    monkeypatch.setattr(ItemService, 'get_items_by_key', fake_get_items_by_key)
    response = client.get('/items/does-not-exist')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Item not found'

def test_get_items_by_restaurant_id_success(monkeypatch):

    async def fake_get_items_by_restaurant_id(_restaurant_id: int):
        return [{'item_name': 'Pad Thai', 'restaurant_id': 2, 'cost': 16.5, 'cuisine': 'Thai', 'times_ordered': 12, 'avg_rating': 4.7, 'dietary': {'vegan': False, 'vegetarian': False, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}}, {'item_name': 'Tom Yum', 'restaurant_id': 2, 'cost': 11.0, 'cuisine': 'Thai', 'times_ordered': 8, 'avg_rating': 4.5, 'dietary': {'vegan': False, 'vegetarian': False, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}}]
    monkeypatch.setattr(ItemService, 'get_items_by_restaurant_id', fake_get_items_by_restaurant_id)
    response = client.get('/items/restaurant/2')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['item_name'] == 'Pad Thai'
    assert data[1]['item_name'] == 'Tom Yum'

def test_update_item_success(monkeypatch):

    async def fake_update_item_by_key(_item_key: str, _item_in):
        return {'item_name': 'Pad Thai', 'restaurant_id': 2, 'cost': 17.0, 'cuisine': 'Thai', 'times_ordered': 13, 'avg_rating': 4.8, 'dietary': {'vegan': False, 'vegetarian': True, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}}
    monkeypatch.setattr(ItemService, 'update_item_by_key', fake_update_item_by_key)
    response = client.patch('/items/Pad Thai', json={'cost': 17.0, 'times_ordered': 13, 'avg_rating': 4.8, 'dietary': {'vegan': False, 'vegetarian': True, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}})
    assert response.status_code == 200
    data = response.json()
    assert data['item_name'] == 'Pad Thai'
    assert data['cost'] == 17.0
    assert data['avg_rating'] == 4.8

def test_update_item_returns_not_found(monkeypatch):

    async def fake_update_item_by_key(_item_key: str, _item_in):
        raise ValueError('Item not found')
    monkeypatch.setattr(ItemService, 'update_item_by_key', fake_update_item_by_key)
    response = client.patch('/items/does-not-exist', json={'cost': 17.0})
    assert response.status_code == 404
    assert response.json()['detail'] == 'Item not found'

def test_create_item_success(monkeypatch):

    async def fake_create_item(_item_in):
        return {'item_name': 'Green Curry', 'restaurant_id': 2, 'cost': 18.5, 'cuisine': 'Thai', 'times_ordered': 0, 'avg_rating': 0.0, 'dietary': {'vegan': False, 'vegetarian': False, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}}
    monkeypatch.setattr(ItemService, 'create_item', fake_create_item)
    response = client.post('/items', json={'item_name': 'Green Curry', 'restaurant_id': 2, 'cost': 18.5, 'cuisine': 'Thai', 'times_ordered': 0, 'avg_rating': 0.0, 'dietary': {'vegan': False, 'vegetarian': False, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}})
    assert response.status_code == 201
    data = response.json()
    assert data['item_name'] == 'Green Curry'
    assert data['restaurant_id'] == 2

def test_create_item_returns_value_error(monkeypatch):

    async def fake_create_item(_item_in):
        raise ValueError('Item already exists')
    monkeypatch.setattr(ItemService, 'create_item', fake_create_item)
    response = client.post('/items', json={'item_name': 'Green Curry', 'restaurant_id': 2, 'cost': 18.5, 'cuisine': 'Thai', 'times_ordered': 0, 'avg_rating': 0.0, 'dietary': {'vegan': False, 'vegetarian': False, 'gluten_free': False, 'dairy_free': False, 'nut_free': False, 'halal': False, 'kosher': False}})
    assert response.status_code == 409
    assert response.json()['detail'] == 'Item already exists'
