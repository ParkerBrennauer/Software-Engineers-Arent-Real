import json
from pathlib import Path
from typing import Any

import aiofiles


class OrderRepo:
    FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "orders.json"

    @classmethod
    async def _read_raw(cls) -> dict[str, dict[str, Any]]:
        if not cls.FILE_PATH.exists():
            return {}

        async with aiofiles.open(cls.FILE_PATH, mode="r") as file:
            raw_orders = await file.read()

        if not raw_orders:
            return {}

        return json.loads(raw_orders)

    @classmethod
    async def read_all(cls) -> dict[str, dict[str, Any]]:
        orders = await cls._read_raw()
        return {
            str(order_id): cls._normalize_order(order_data)
            for order_id, order_data in orders.items()
        }

    @staticmethod
    def _normalize_order(order_data: dict[str, Any]) -> dict[str, Any]:
        normalized_order = dict(order_data)

        if "order_satus" in normalized_order and "order_status" not in normalized_order:
            normalized_order["order_status"] = normalized_order.pop("order_satus")

        return normalized_order

    @classmethod
    async def get_by_id(cls, order_id: str) -> dict[str, Any] | None:
        orders = await cls.read_all()
        return orders.get(str(order_id))

    @classmethod
    async def update_order(
        cls, order_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        orders = await cls._read_raw()
        normalized_order_id = str(order_id)

        if normalized_order_id not in orders:
            return None

        existing_order = orders[normalized_order_id]
        persisted_updates = dict(updates)
        if (
            "order_status" in persisted_updates
            and "order_satus" in existing_order
            and "order_status" not in existing_order
        ):
            persisted_updates["order_satus"] = persisted_updates.pop("order_status")

        existing_order.update(persisted_updates)

        async with aiofiles.open(cls.FILE_PATH, mode="w") as file:
            await file.write(json.dumps(orders, indent=4))

        return cls._normalize_order(orders[normalized_order_id])
