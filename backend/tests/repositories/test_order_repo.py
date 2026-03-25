import json

import pytest

from src.repositories.order_repo import OrderRepo
from src.schemas.order_schema import OrderStatus


@pytest.mark.asyncio
async def test_update_order_persists_order_status_updates(
    monkeypatch, tmp_path
):
    file_path = tmp_path / "orders.json"
    file_path.write_text(
        json.dumps(
            {
                "1": {
                    "restaurant": "Restaurant_1",
                    "customer": "customer_1",
                    "distance": 2.0,
                    "time": 10,
                    "order_status": OrderStatus.PAYMENT_PENDING.value,
                },
                "2": {
                    "restaurant": "Restaurant_2",
                    "customer": "customer_2",
                    "distance": 4.0,
                    "time": 15,
                    "order_status": OrderStatus.PAYMENT_PENDING.value,
                },
            },
            indent=4,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(OrderRepo, "FILE_PATH", file_path)

    updated_order = await OrderRepo.update_order(
        "1",
        {"order_status": OrderStatus.OUT_FOR_DELIVERY.value},
    )

    saved_orders = json.loads(file_path.read_text(encoding="utf-8"))

    assert updated_order["order_status"] == OrderStatus.OUT_FOR_DELIVERY.value
    assert saved_orders["1"]["order_status"] == OrderStatus.OUT_FOR_DELIVERY.value
    assert saved_orders["2"]["order_status"] == OrderStatus.PAYMENT_PENDING.value
