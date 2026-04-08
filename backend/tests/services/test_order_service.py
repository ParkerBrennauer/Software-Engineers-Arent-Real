from unittest.mock import AsyncMock, patch
from src.services.order_services import OrderService
from src.schemas.order_schema import Order
import pytest

@pytest.mark.asyncio
async def test_get_order_status():
    fake_order = Order(items=['Spaghetti'], cost=20.0, restaurant="Trevor's pasta", customer='Joe', time=20, cuisine='Italian', distance=2.5)
    with patch('src.repositories.order_repo.OrderRepo.get_order', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_order
        order = await OrderService.get_order_status('123')
        assert order == fake_order

@pytest.mark.asyncio
async def test_cancel_order():
    with patch('src.repositories.order_repo.OrderRepo.update_order', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = 'cancelled'
        result = await OrderService.cancel_order('123')
        assert result == 'cancelled'
        mock_update.assert_called_once()
        assert mock_update.call_args[0][0] == '123'

@pytest.mark.asyncio
async def test_get_restaurant_orders():
    fake_orders = {'1': {'items': ['Spaghetti'], 'cost': 20.0, 'restaurant': "Trevor's pasta", 'customer': 'Joe', 'time': 20, 'cuisine': 'Italian', 'distance': 2.5}, '2': {'items': ['Burger'], 'cost': 15.0, 'restaurant': 'MD', 'customer': 'Mike', 'time': 15, 'cuisine': 'American', 'distance': 7.5}}
    with patch('src.repositories.order_repo.OrderRepo.get_all_orders', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_orders
        orders = await OrderService.get_restaurant_orders("Trevor's pasta")
        assert orders[0].restaurant == "Trevor's pasta"

@pytest.mark.asyncio
async def test_mark_ready_for_pickup():
    with patch('src.repositories.order_repo.OrderRepo.update_order', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = 'updated_order'
        result = await OrderService.mark_ready_for_pickup('123')
        assert result == 'updated_order'
        mock_update.assert_called_once()
        assert mock_update.call_args[0][0] == '123'

@pytest.mark.asyncio
async def test_report_restaurant_delay():
    with patch('src.repositories.order_repo.OrderRepo.update_order', new_callable=AsyncMock) as mock_update, patch('src.repositories.order_repo.OrderRepo.get_order', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Order(items=['Spaghetti'], cost=20.0, restaurant="Trevor's pasta", customer='Joe', time=20, cuisine='Italian', distance=2.5, order_status='preparing')
        mock_update.return_value = 'delayed'
        result = await OrderService.report_restaurant_delay('123', 'Busy restaurant')
        assert result == 'delayed'
        mock_update.assert_called_once()
        assert mock_update.call_args[0][0] == '123'

@pytest.mark.asyncio
async def test_assign_driver():
    with patch('src.repositories.order_repo.OrderRepo.update_order', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = 'updated_order'
        result = await OrderService.assign_driver('123', 'driver1')
        assert result == 'updated_order'
        mock_update.assert_called_once()
        args = mock_update.call_args[0]
        assert args[0] == '123'

@pytest.mark.asyncio
async def test_get_driver_orders():
    with patch('src.repositories.order_repo.OrderRepo.get_orders_by_driver', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = ['order1', 'order2']
        orders = await OrderService.get_driver_orders('driver1')
        assert len(orders) == 2

@pytest.mark.asyncio
async def test_pickup_order():
    with patch('src.repositories.order_repo.OrderRepo.update_order', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = 'picked_up'
        result = await OrderService.pickup_order('123')
        mock_update.assert_called_once()
        assert result == 'picked_up'

@pytest.mark.asyncio
async def test_report_driver_delay():
    with patch('src.repositories.order_repo.OrderRepo.update_order', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = 'driver_delayed'
        result = await OrderService.report_driver_delay('123', 'Busy traffic')
        assert result == 'driver_delayed'
        mock_update.assert_called_once()
        assert mock_update.call_args[0][0] == '123'

@pytest.mark.asyncio
async def test_refund_success():
    fake_order = Order(items=['Spaghetti'], cost=20.0, restaurant="Trevor's pasta", customer='Joe', time=20, cuisine='Italian', distance=2.5, order_status='delayed', payment_status='accepted')
    with patch('src.repositories.order_repo.OrderRepo.get_order', new_callable=AsyncMock) as mock_get, patch('src.repositories.order_repo.OrderRepo.update_order', new_callable=AsyncMock) as mock_update:
        mock_get.return_value = fake_order
        mock_update.return_value = fake_order
        result = await OrderService.process_refund('123')
        assert result is not None
        mock_update.assert_called_once()

@pytest.mark.asyncio
async def test_refund_already_issued():
    fake_order = Order(items=['Spaghetti'], cost=20.0, restaurant="Trevor's pasta", customer='Joe', time=20, cuisine='Italian', distance=2.5, order_status='delayed', payment_status='accepted', refund_issued=True)
    with patch('src.repositories.order_repo.OrderRepo.get_order', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_order
        with pytest.raises(ValueError):
            await OrderService.process_refund('123')

@pytest.mark.asyncio
async def test_refund_not_applicable():
    fake_order = Order(items=['Spaghetti'], cost=20.0, restaurant="Trevor's pasta", customer='Joe', time=20, cuisine='Italian', distance=2.5, order_status='delivered', payment_status='accepted')
    with patch('src.repositories.order_repo.OrderRepo.get_order', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_order
        with pytest.raises(ValueError):
            await OrderService.process_refund('123')
