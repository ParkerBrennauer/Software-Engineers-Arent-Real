import pytest
from src.services import OrderService
from src.repositories import OrderRepo


async def test_update_order_success():
    existing_order = {
        "id": 5,
        "order_status": "payment pending",
        "payment_status": "pending",
        "items": [{"id": 1, "price": 10.0}],
        "cost": 10.0,
        "locked": False,
    }

    update_data = {
        "items": [
            {"id": 1, "price": 10.0},
            {"id": 2, "price": 5.0},
        ]
    }

    captured = {}

    async def fake_get_by_id(_id: int):
        return existing_order

    async def fake_update_order(_id: int, data: dict):
        captured["payload"] = data
        return data

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderRepo, "update_order", fake_update_order)

    updated = await OrderService.update_order(5, update_data)

    assert updated.id == 5
    assert updated.cost == 16.95
    assert len(updated.items) == 2

    payload = captured["payload"]
    assert payload["cost"] == 16.95
    assert payload["items"] == update_data["items"]

    monkeypatch.undo()


async def test_update_order_locked():
    existing_order = {"id": 5, "locked": True}

    async def fake_get_by_id(_id: int):
        return existing_order

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    with pytest.raises(ValueError, match="locked"):
        await OrderService.update_order(5, {"items": []})

    monkeypatch.undo()


async def test_update_order_delivery_instructions():
    existing_order = {
        "id": 5,
        "order_status": "payment pending",
        "payment_status": "pending",
        "items": [],
        "cost": 0.0,
        "locked": False,
    }

    update_data = {"delivery_instructions": "Call upon arrival"}

    captured = {}

    async def fake_get_by_id(_id: int):
        return existing_order

    async def fake_update_order(_id: int, data: dict):
        captured["payload"] = data
        return data

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderRepo, "update_order", fake_update_order)

    updated = await OrderService.update_order(5, update_data)

    payload = captured["payload"]
    assert payload["delivery_instructions"] == "Call upon arrival"
    assert updated.delivery_instructions == "Call upon arrival"

    monkeypatch.undo()
