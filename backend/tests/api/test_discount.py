from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from src.api.dependencies import get_current_user
from src.main import app
client = TestClient(app)

@pytest.fixture(autouse=True)
def _discount_owner_auth():

    async def fake_current_user():
        return {'id': 1, 'role': 'owner', 'restaurant_id': 1}
    app.dependency_overrides[get_current_user] = fake_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

@patch('src.api.routers.discount_router.DiscountServices.createDiscount', new_callable=AsyncMock)
def test_create_discount_success(mock_create_discount):
    mock_create_discount.return_value = 'valid code, enjoy saving'
    response = client.post('/discounts/', json={'discount_rate': 0.1, 'discount_code': 'SAVE10', 'restaurant_id': 1})
    assert response.status_code == 200
    assert response.json() == {'message': 'valid code, enjoy saving'}
    mock_create_discount.assert_awaited_once_with(0.1, 'SAVE10', 1)

@patch('src.api.routers.discount_router.DiscountServices.createDiscount', new_callable=AsyncMock)
def test_create_discount_invalid(mock_create_discount):
    mock_create_discount.return_value = 'code is invalid'
    response = client.post('/discounts/', json={'discount_rate': 0.1, 'discount_code': 'SAVE10', 'restaurant_id': 1})
    assert response.status_code == 400
    assert response.json() == {'detail': 'code is invalid'}
    mock_create_discount.assert_awaited_once_with(0.1, 'SAVE10', 1)

@patch('src.api.routers.discount_router.DiscountServices.applyDiscount', new_callable=AsyncMock)
def test_apply_discount_success(mock_apply_discount):
    mock_apply_discount.return_value = 80.0
    response = client.post('/discounts/apply', json={'order_total': 100.0, 'discount_code': 'SAVE20'})
    assert response.status_code == 200
    assert response.json() == {'discounted_total': 80.0}
    mock_apply_discount.assert_awaited_once_with(100.0, 'SAVE20')

@patch('src.api.routers.discount_router.DiscountServices.applyDiscount', new_callable=AsyncMock)
def test_apply_discount_not_found(mock_apply_discount):
    mock_apply_discount.return_value = None
    response = client.post('/discounts/apply', json={'order_total': 100.0, 'discount_code': 'BADCODE'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Discount not found'}
    mock_apply_discount.assert_awaited_once_with(100.0, 'BADCODE')

@patch('src.api.routers.discount_router.DiscountServices.removeDiscount', new_callable=AsyncMock)
@patch('src.api.routers.discount_router.DiscountServices.get_discount', new_callable=AsyncMock)
def test_remove_discount_success(mock_get_discount, mock_remove_discount):
    mock_get_discount.return_value = {'restaurant_id': 1, 'discount_rate': 0.1}
    mock_remove_discount.return_value = 'successfully removed code'
    response = client.delete('/discounts/SAVE10')
    assert response.status_code == 200
    assert response.json() == {'message': 'successfully removed code'}
    mock_get_discount.assert_awaited_once_with('SAVE10')
    mock_remove_discount.assert_awaited_once_with('SAVE10')

@patch('src.api.routers.discount_router.DiscountServices.removeDiscount', new_callable=AsyncMock)
@patch('src.api.routers.discount_router.DiscountServices.get_discount', new_callable=AsyncMock)
def test_remove_discount_not_found(mock_get_discount, mock_remove_discount):
    mock_get_discount.return_value = None
    response = client.delete('/discounts/SAVE10')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Discount not found'}
    mock_get_discount.assert_awaited_once_with('SAVE10')
    mock_remove_discount.assert_not_awaited()
