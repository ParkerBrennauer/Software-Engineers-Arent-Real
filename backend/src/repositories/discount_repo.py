import json
from typing import Optional
import aiofiles
from src.core.config import DISCOUNT_FILE

class DiscountRepo:
    FILE_PATH = DISCOUNT_FILE

    @classmethod
    async def read_all(cls) -> dict:

        if not cls.FILE_PATH.exists():
            return {}

        async with aiofiles.open(cls.FILE_PATH, mode="r") as f:
            discounts = await f.read()
            if not discounts:
                return {}

            return json.loads(discounts)

    @classmethod
    async def write_all(cls, data: dict) -> None:
        async with aiofiles.open(cls.FILE_PATH, "w") as f:
            await f.write(json.dumps(data, indent=1))

    @classmethod
    async def find_code(cls, discount_code : str) -> Optional[dict]:
        code = await cls.read_all()
        return code.get(discount_code)

    @classmethod
    async def save_code(cls, discount_data: dict) -> dict:
        data = await cls.read_all()

        for discount_code, details in discount_data.items():
            if discount_code not in data:
                data[discount_code] = details
            else:
                data[discount_code].update(details)

        await cls.write_all(data)

        return discount_data

    @classmethod
    async def find_savings(cls, discount_code : str) -> Optional[float]:
        code = await cls.find_code(discount_code)
        if code is not None:
            return code["discount_rate"]
        return None

    @classmethod
    async def check_real(cls, discount_code : str) -> bool:
        code = await cls.find_code(discount_code)
        return code is not None

    @classmethod
    async def remove_code(cls, discount_code: str):
        data = await cls.read_all()

        if discount_code not in data:
            return False

        del data[discount_code]
        await cls.write_all(data)

        return True