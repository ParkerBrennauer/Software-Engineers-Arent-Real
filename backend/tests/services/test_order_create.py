import pytest
from src.schemas import order_schema
from src.services import OrderService
from src.repositories import OrderRepo

async def test_create_order_success():
    order_in = order_schema.OrderCreate(
        id = 0,
        restaurant="Test Restaurant",
        customer="test_customer",
        time=30,
        cuisine="testfood",
        distance=2,
        items=[
            {"id": 1, "price": 10.0},
            {"id": 2, "price": 5.5},
        ]
    )

    captured = {}

    async def fake_get_largest_order_id():
        return 7

    async def fake_save_order(order_data: dict):
        captured["payload"] = order_data
        return order_data

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(OrderRepo, "get_largest_order_id", fake_get_all_orders)
    monkeypatch.setattr(OrderRepo, "save_order", fake_save_order)

    created = await OrderService.create_order(order_in)

    assert created.id == 8
    payload = captured["payload"]
    assert payload["order_status"] == "payment pending"
    assert payload["payment_status"] == "pending"
    assert payload["locked"] is False
    assert payload["cost"] == 17.52
    assert payload["items"] == [
        {"id": 1, "price": 10.0},
        {"id": 2, "price": 5.5},
    ]

    monkeypatch.undo()