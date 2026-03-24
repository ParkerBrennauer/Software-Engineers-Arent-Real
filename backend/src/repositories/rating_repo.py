import json
from pathlib import Path
from typing import Any

import aiofiles


class RatingRepo:
    FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "reviews.json"

    @classmethod
    async def read_all(cls) -> dict[str, dict[str, Any]]:
        if not cls.FILE_PATH.exists():
            return {}

        async with aiofiles.open(cls.FILE_PATH, mode="r") as file:
            raw_reviews = await file.read()

        if not raw_reviews:
            return {}

        return json.loads(raw_reviews)

    @classmethod
    async def get_by_order_id(cls, order_id: str) -> dict[str, Any] | None:
        reviews = await cls.read_all()
        return reviews.get(order_id)

    @classmethod
    async def update_submitted_rating(
        cls, order_id: str, stars: int
    ) -> dict[str, Any] | None:
        reviews = await cls.read_all()

        if order_id not in reviews:
            return None

        reviews[order_id]["submitted_stars"] = stars

        async with aiofiles.open(cls.FILE_PATH, mode="w") as file:
            await file.write(json.dumps(reviews, indent=1))

        return reviews[order_id]
