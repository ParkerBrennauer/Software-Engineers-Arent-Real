import pytest
from src.services.tips_service import TipService
from unittest.mock import AsyncMock, patch

def test_calculate_tip_percent():
    result = TipService.calculate_tip(100, tip_percent=10)
    assert result == 10.0

def test_calculate_tip_fixed():
    result = TipService.calculate_tip(100, tip_amount=15)
    assert result == 15.0

def test_calculate_tip_both_provided():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100, tip_percent=10, tip_amount=5)

def test_calculate_tip_negative_percent():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100, tip_percent=-5)

def test_calculate_tip_negative_amount():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100, tip_amount=-10)

def test_calculate_tip_missing_inputs():
    with pytest.raises(ValueError):
        TipService.calculate_tip(100)

@pytest.mark.asyncio
@patch('src.services.tips_service.OrderService')
async def test_apply_tip_percent(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value={'id': 1, 'cost': 100, 'payment_status': 'accepted'})
    mock_order_service.update_order = AsyncMock(return_value={'id': 1, 'tip_percent': 10, 'tip_amount': 10})
    result = await TipService.apply_tip(1, tip_percent=10)
    assert result['tip_amount'] == 10
    mock_order_service.update_order.assert_called_once()

@pytest.mark.asyncio
@patch('src.services.tips_service.OrderService')
async def test_apply_tip_fixed(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value={'id': 1, 'cost': 100, 'payment_status': 'accepted'})
    mock_order_service.update_order = AsyncMock(return_value={'id': 1, 'tip_amount': 20})
    result = await TipService.apply_tip(1, tip_amount=20)
    assert result['tip_amount'] == 20

@pytest.mark.asyncio
@patch('src.services.tips_service.OrderService')
async def test_apply_tip_order_not_found(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value=None)
    with pytest.raises(ValueError):
        await TipService.apply_tip(1, tip_percent=10)
