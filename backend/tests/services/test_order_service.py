from src.services.order_services import OrderService
from src.schemas.order_schema import Order
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_order_status():

    fake_order = Order(
        items=["Pizza"],
        cost=25.0,
        restaurant="Joe's pizza",
        customer="Trevor",
        time=20,
        cuisine="Italian",
        distance=5.0,
    )

    with patch("src.repositories.order_repo.OrderRepo.get_order", new_callable=AsyncMock) as mock_get:

        mock_get.return_value = fake_order
        order = await OrderService.get_order_status("123")
        assert order == fake_order

@pytest.mark.asyncio
async def test_mark_ready_for_pickup():
    