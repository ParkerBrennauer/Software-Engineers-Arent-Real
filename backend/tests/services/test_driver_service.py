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

