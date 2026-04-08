import json
from typing import Any
import aiofiles
from src.core.config import ORDERS_FILE

class OrderRepo:
    FILE_PATH = ORDERS_FILE

    @classmethod
    async def _read_raw(cls) -> dict[str, dict[str, Any]]:
        if not cls.FILE_PATH.exists():
            return {}
        async with aiofiles.open(cls.FILE_PATH, mode='r') as file:
            raw_orders = await file.read()
        if not raw_orders:
            return {}
        return json.loads(raw_orders)

    @staticmethod
    def _with_order_id(order_id: str, order_data: dict[str, Any]) -> dict[str, Any]:
        hydrated_order = dict(order_data)
        hydrated_order.setdefault('id', int(order_id))
        return hydrated_order

    @staticmethod
    def _prepare_for_storage(order_data: dict[str, Any]) -> dict[str, Any]:
        persisted_order = dict(order_data)
        persisted_order.pop('id', None)
        return persisted_order

    @classmethod
    async def _write_raw(cls, orders: dict[str, dict[str, Any]]) -> None:
        async with aiofiles.open(cls.FILE_PATH, mode='w') as file:
            await file.write(json.dumps(orders, indent=4))

    @classmethod
    async def get_by_id(cls, order_id: int | str) -> dict[str, Any] | None:
        orders = await cls._read_raw()
        order_data = orders.get(str(order_id))
        if order_data is None:
            return None
        return cls._with_order_id(str(order_id), order_data)

    @classmethod
    async def save_order(cls, order_data: dict[str, Any]) -> dict[str, Any]:
        orders = await cls._read_raw()
        order_id = str(order_data.get('id', await cls.get_largest_order_id() + 1))
        orders[order_id] = cls._prepare_for_storage(order_data)
        await cls._write_raw(orders)
        return cls._with_order_id(order_id, orders[order_id])

    @classmethod
    async def update_order(cls, order_id: int | str, updated_data: dict[str, Any]) -> dict[str, Any] | None:
        orders = await cls._read_raw()
        normalized_order_id = str(order_id)
        if normalized_order_id not in orders:
            return None
        existing_order = orders[normalized_order_id]
        merged_order = {**existing_order, **dict(updated_data)}
        orders[normalized_order_id] = cls._prepare_for_storage(merged_order)
        await cls._write_raw(orders)
        return cls._with_order_id(normalized_order_id, orders[normalized_order_id])

    @classmethod
    async def get_largest_order_id(cls) -> int:
        orders = await cls._read_raw()
        if not orders:
            return 0
        largest_key_id = max((int(order_id) for order_id in orders), default=0)
        largest_embedded_id = max((int(order.get('id', 0)) for order in orders.values() if str(order.get('id', '')).isdigit()), default=0)
        return max(largest_key_id, largest_embedded_id)

    @classmethod
    async def get_orders_by_driver(cls, driver: str) -> list[dict[str, Any]]:
        orders = await cls._read_raw()
        return [cls._with_order_id(str(order_id), order) for order_id, order in orders.items() if order.get('driver') == driver]

    @classmethod
    async def get_order(cls, order_id: int | str) -> dict[str, Any] | None:
        return await cls.get_by_id(order_id)

    @classmethod
    async def get_all_orders(cls) -> dict[str, dict[str, Any]]:
        orders = await cls._read_raw()
        return {str(order_id): cls._with_order_id(str(order_id), order_data) for order_id, order_data in orders.items()}

    @classmethod
    async def get_orders_by_status(cls, status: str) -> list[dict[str, Any]]:
        orders = await cls._read_raw()
        return [cls._with_order_id(str(order_id), order) for order_id, order in orders.items() if order.get('order_status') == status]

    @classmethod
    async def get_orders_by_date_range(cls, start_time: int, end_time: int) -> list[dict[str, Any]]:
        orders = await cls._read_raw()
        return [cls._with_order_id(str(order_id), order) for order_id, order in orders.items() if start_time <= order.get('time', 0) <= end_time]

    @classmethod
    async def get_orders_by_status_and_date(cls, status: str, start_time: int, end_time: int) -> list[dict[str, Any]]:
        orders = await cls._read_raw()
        return [cls._with_order_id(str(order_id), order) for order_id, order in orders.items() if order.get('order_status') == status and start_time <= order.get('time', 0) <= end_time]
