import pytest
from unittest.mock import AsyncMock, patch
from src.services.driver_service import DriverService

@pytest.mark.asyncio
@patch("src.services.driver_service.OrderService")
async def test_tip_driver_success(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value={
        "id": 1,
        "tip_amount": 10,
        "driver": "driver_1",
        "tip_paid": False
    })

    mock_order_service.update_order = AsyncMock()

    result = await DriverService.tip_driver(1)

    assert result["status"] == "paid"
    assert result["amount"] == 10

    mock_order_service.update_order.assert_called_once_with(1, {"tip_paid": True})

@pytest.mark.asyncio
@patch("src.services.driver_service.OrderService")
async def test_tip_driver_no_tip(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value={
        "tip_amount": 0,
        "driver": "driver_1",
    })

    with pytest.raises(ValueError):
        await DriverService.tip_driver(1)

@pytest.mark.asyncio
@patch("src.services.driver_service.OrderService")
async def test_tip_driver_already_paid(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value={
        "tip_amount": 10,
        "driver": "driver_1",
        "tip_paid": True
    })

    with pytest.raises(ValueError):
        await DriverService.tip_driver(1)

@pytest.mark.asyncio
@patch("src.services.driver_service.OrderService")
async def test_tip_driver_no_driver(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value={
        "tip_amount": 10,
        "driver": None,
        "tip_paid": False
    })

    with pytest.raises(ValueError):
        await DriverService.tip_driver(1)

@pytest.mark.asyncio
@patch("src.services.driver_service.OrderService")
async def test_tip_driver_order_not_found(mock_order_service):
    mock_order_service.get_order_status = AsyncMock(return_value=None)

    with pytest.raises(ValueError):
        await DriverService.tip_driver(1)