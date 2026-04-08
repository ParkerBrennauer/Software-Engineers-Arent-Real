import json
from typing import Any
import aiofiles
from src.core.config import CUSTOMERS_FILE

class CustomerRepo:
    FILE_PATH = CUSTOMERS_FILE

    @classmethod
    async def read_all(cls) -> dict[str, dict[str, Any]]:
        if not cls.FILE_PATH.exists():
            return {}
        async with aiofiles.open(cls.FILE_PATH, mode='r') as file:
            raw_customers = await file.read()
        if not raw_customers:
            return {}
        return json.loads(raw_customers)

    @classmethod
    async def get_by_id(cls, customer_id: str) -> dict[str, Any] | None:
        customers = await cls.read_all()
        return customers.get(customer_id)

    @classmethod
    async def update_by_id(cls, customer_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        customers = await cls.read_all()
        if customer_id not in customers:
            return None
        customers[customer_id].update(updates)
        async with aiofiles.open(cls.FILE_PATH, mode='w') as file:
            await file.write(json.dumps(customers, indent=1))
        return customers[customer_id]
