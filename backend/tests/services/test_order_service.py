from unittest.mock import AsyncMock, patch
from src.services.order_services import OrderService
from src.schemas.order_schema import Order
import pytest

@pytest.mark.asyncio
async def test_get_order_status():

    fake_order = Order(
        items=["Pizza"],
        cost=20.0,
        restaurant="Trevor's pasta",
        customer="Joe",
        time=20,
        cuisine="spaghetti",
        distance=2.5,
    )

    with patch("src.repositories.order_repo.OrderRepo.get_order",
                new_callable=AsyncMock) as mock_get:

        mock_get.return_value = fake_order
        order = await OrderService.get_order_status("123")
        assert order == fake_order

@pytest.mark.asyncio
async def test_mark_ready_for_pickup():

    with patch("src.repositories.order_repo.OrderRepo.update_order",
                new_callable=AsyncMock) as mock_update:

        mock_update.return_value = "updated_order"
        result = await OrderService.mark_ready_for_pickup("123")
        mock_update.assert_called_once()
        assert result == "updated_order"

@pytest.mark.asyncio
async def test_assign_driver():

    with patch("src.repositories.order_repo.OrderRepo.update_order",
                new_callable=AsyncMock) as mock_update:

        mock_update.return_value = "updated_order"
        await OrderService.assign_driver("123", "driver1")
        mock_update.assert_called_once()
        args = mock_update.call_args[0]
        assert args[0] == "123"

@pytest.mark.asyncio
async def test_get_driver_orders():

    with patch("src.repositories.order_repo.OrderRepo.get_orders_by_driver",
                new_callable=AsyncMock) as mock_get:

        mock_get.return_value = ["order1", "order2"]
        orders = await OrderService.get_driver_orders("driver1")
        assert len(orders) == 2

@pytest.mark.asyncio
async def test_cancel_order():

    with patch("src.repositories.order_repo.OrderRepo.update_order",
                new_callable=AsyncMock) as mock_update:

        mock_update.return_value = "cancelled"
        result = await OrderService.cancel_order("123")
        mock_update.assert_called_once()
        assert result == "cancelled"

@pytest.mark.asyncio
async def test_get_restaurant_orders():

    fake_orders = {
        "1" : {"restaurant": "Trevor's pasta"},
        "2" : {"restaurant": "Other restaurants"}
    }

    with patch("src.repositories.order_repo.OrderRepo.get_all_orders",
               new_callable=AsyncMock) as mock_get:

        mock_get.return_value = fake_orders
        orders = await OrderService.get_restaurant_orders("Trevor's pasta")
        assert len(orders) == 1

@pytest.mark.asyncio
async def test_report_restaurant_delay():

    with patch("src.repositories.order_repo.OrderRepo.update_order",
               new_callable=AsyncMock) as mock_update:
        
        mock_update.return_value = "delayed"
        result = await OrderService.report_restaurant_delay("123", "Busy restaurant")
        mock_update.assert_called_once()
        assert result == "delayed"

@pytest.mark.asyncio
async def test_pickup_order():

    with patch("src.repositories.order_repo.OrderRepo.update_order",
               new_callable=AsyncMock) as mock_update:

        mock_update.return_value = "picked_up"
        result = await OrderService.pickup_order("123")
        mock_update.assert_called_once()
        assert result == "picked_up"

@pytest.mark.asyncio
async def test_report_driver_delay():

    with patch("src.repositories.order_repo.OrderRepo.update_order",
               new_callable=AsyncMock) as mock_update:
        
        mock_update.return_value = "driver_delayed"
        result = await OrderService.report_driver_delay("123", "Busy traffic")
        mock_update.assert_called_once()
        assert result == "driver_delayed"
