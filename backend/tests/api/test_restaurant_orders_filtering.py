import pytest
from fastapi import status
from src.schemas.order_schema import Order

def _mock_orders():
    return [Order(id=1, items=['Pizza'], cost=16.95, restaurant='Pizza', customer='c1', time=100, cuisine='Italian', distance=2.5, order_status='confirmed', payment_status='accepted')]

@pytest.mark.asyncio
async def test_filter_by_status_success(client, monkeypatch):

    async def mock(_restaurant_id, _username, _status):
        return _mock_orders()
    monkeypatch.setattr('src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders_by_status', mock)
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/status?username=owner1&order_status=confirmed')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_filter_by_status_permission_denied(client, monkeypatch):

    async def mock(*_):
        raise ValueError("User does not have permission to view this restaurant's orders")
    monkeypatch.setattr('src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders_by_status', mock)
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/status?username=customer1&order_status=confirmed')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_filter_by_status_user_not_found(client, monkeypatch):

    async def mock(*_):
        raise ValueError('User not found')
    monkeypatch.setattr('src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders_by_status', mock)
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/status?username=nonexistent&order_status=confirmed')
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_filter_by_date_range_success(client, monkeypatch):

    async def mock(*_):
        return _mock_orders()
    monkeypatch.setattr('src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders_by_date_range', mock)
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/date?username=owner1&start_time=100&end_time=200')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_filter_by_date_range_no_results(client, monkeypatch):

    async def mock(*_):
        return []
    monkeypatch.setattr('src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders_by_date_range', mock)
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/date?username=owner1&start_time=1000&end_time=2000')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0

@pytest.mark.asyncio
async def test_filter_by_status_and_date_success(client, monkeypatch):

    async def mock(*_):
        return _mock_orders()
    monkeypatch.setattr('src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders_by_status_and_date', mock)
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/status-and-date?username=owner1&order_status=confirmed&start_time=100&end_time=200')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_filter_by_status_missing_params(client):
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/status?order_status=confirmed')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_filter_by_date_missing_params(client):
    response = client.get('/restaurant_administration/restaurants/10/orders/filter/date?username=owner1&end_time=200')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_filter_by_status_and_date_restaurant_not_found(client, monkeypatch):

    async def mock(*_):
        raise ValueError('Restaurant not found')
    monkeypatch.setattr('src.api.routers.restaurant_administration_router.RestaurantOwnerService.get_restaurant_orders_by_status_and_date', mock)
    response = client.get('/restaurant_administration/restaurants/999/orders/filter/status-and-date?username=owner1&order_status=confirmed&start_time=100&end_time=200')
    assert response.status_code == status.HTTP_404_NOT_FOUND
