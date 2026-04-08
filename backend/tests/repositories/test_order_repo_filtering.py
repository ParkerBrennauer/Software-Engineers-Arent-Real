import json
import pytest
from src.repositories.order_repo import OrderRepo
from src.schemas.order_schema import OrderStatus

def _orders_fixture():
    return {'1': {'restaurant': 'R1', 'customer': 'c1', 'time': 100, 'order_status': OrderStatus.PAYMENT_PENDING.value}, '2': {'restaurant': 'R2', 'customer': 'c2', 'time': 200, 'order_status': OrderStatus.CONFIRMED.value}, '3': {'restaurant': 'R1', 'customer': 'c3', 'time': 150, 'order_status': OrderStatus.PAYMENT_PENDING.value}}

@pytest.mark.asyncio
async def test_get_orders_by_status(monkeypatch, tmp_path):
    file_path = tmp_path / 'orders.json'
    file_path.write_text(json.dumps(_orders_fixture()), encoding='utf-8')
    monkeypatch.setattr(OrderRepo, 'FILE_PATH', file_path)
    orders = await OrderRepo.get_orders_by_status(OrderStatus.PAYMENT_PENDING.value)
    assert len(orders) == 2
    assert all((o['order_status'] == OrderStatus.PAYMENT_PENDING.value for o in orders))

@pytest.mark.asyncio
async def test_get_orders_by_status_no_matches(monkeypatch, tmp_path):
    file_path = tmp_path / 'orders.json'
    file_path.write_text(json.dumps(_orders_fixture()), encoding='utf-8')
    monkeypatch.setattr(OrderRepo, 'FILE_PATH', file_path)
    orders = await OrderRepo.get_orders_by_status(OrderStatus.DELIVERED.value)
    assert len(orders) == 0

@pytest.mark.asyncio
async def test_get_orders_by_date_range(monkeypatch, tmp_path):
    file_path = tmp_path / 'orders.json'
    file_path.write_text(json.dumps(_orders_fixture()), encoding='utf-8')
    monkeypatch.setattr(OrderRepo, 'FILE_PATH', file_path)
    orders = await OrderRepo.get_orders_by_date_range(100, 200)
    assert len(orders) == 3
    assert all((100 <= o['time'] <= 200 for o in orders))

@pytest.mark.asyncio
async def test_get_orders_by_status_and_date(monkeypatch, tmp_path):
    file_path = tmp_path / 'orders.json'
    file_path.write_text(json.dumps(_orders_fixture()), encoding='utf-8')
    monkeypatch.setattr(OrderRepo, 'FILE_PATH', file_path)
    orders = await OrderRepo.get_orders_by_status_and_date(OrderStatus.PAYMENT_PENDING.value, 100, 200)
    assert len(orders) == 2
    assert all((o['order_status'] == OrderStatus.PAYMENT_PENDING.value and 100 <= o['time'] <= 200 for o in orders))
