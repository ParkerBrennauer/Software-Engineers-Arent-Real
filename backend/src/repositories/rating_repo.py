import json
from pathlib import Path
from typing import Any

import aiofiles


class RatingRepo:
    FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "reviews.json"
    RESTAURANTS_FILE_PATH = (
        Path(__file__).resolve().parent.parent / "data" / "restaurants.json"
    )

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

    @classmethod
    async def read_restaurants(cls) -> dict[str, dict[str, Any]]:
        if not cls.RESTAURANTS_FILE_PATH.exists():
            return {}

        async with aiofiles.open(cls.RESTAURANTS_FILE_PATH, mode="r") as file:
            raw_restaurants = await file.read()

        if not raw_restaurants:
            return {}

        return json.loads(raw_restaurants)

    @classmethod
    async def get_restaurant_id_by_order_id(cls, order_id: str) -> int | None:
        restaurants = await cls.read_restaurants()

        for restaurant_id, restaurant_data in restaurants.items():
            if order_id in restaurant_data.get("order_ids", []):
                return int(restaurant_id)

        return None

    @classmethod
    async def update_review_text(
        cls, order_id: str, review_text: str
    ) -> dict[str, Any] | None:
        reviews = await cls.read_all()

        if order_id not in reviews:
            return None

        reviews[order_id]["review_text"] = review_text

        async with aiofiles.open(cls.FILE_PATH, mode="w") as file:
            await file.write(json.dumps(reviews, indent=1))

        return reviews[order_id]
