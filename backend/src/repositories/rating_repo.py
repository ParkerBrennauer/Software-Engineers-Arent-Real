import json
from typing import Any
import aiofiles
from src.core.config import REVIEWS_FILE, RESTAURANTS_FILE, REPORTS_FILE
from src.repositories.order_repo import OrderRepo

class RatingRepo:
    FILE_PATH = REVIEWS_FILE
    RESTAURANTS_FILE_PATH = RESTAURANTS_FILE
    REPORTS_FILE_PATH = REPORTS_FILE

    @classmethod
    async def read_all(cls) -> dict[str, dict[str, Any]]:
        if not cls.FILE_PATH.exists():
            return {}
        async with aiofiles.open(cls.FILE_PATH, mode='r') as file:
            raw_reviews = await file.read()
        if not raw_reviews:
            return {}
        return json.loads(raw_reviews)

    @classmethod
    async def get_by_order_id(cls, order_id: str) -> dict[str, Any] | None:
        reviews = await cls.read_all()
        review = reviews.get(order_id)
        order = await OrderRepo.get_by_id(order_id)
        if review is None and order is None:
            return None
        if review is None:
            return order
        if order is None:
            return review
        return {**order, **review}

    @classmethod
    async def _ensure_review_entry(
        cls, reviews: dict[str, dict[str, Any]], order_id: str
    ) -> dict[str, Any] | None:
        existing_review = reviews.get(order_id)
        if existing_review is not None:
            return existing_review

        order = await OrderRepo.get_by_id(order_id)
        if order is None:
            return None

        review_entry = {
            "customer": order.get("customer"),
            "restaurant": order.get("restaurant"),
            "submitted_stars": None,
            "review_text": None,
        }
        reviews[order_id] = review_entry
        return review_entry

    @classmethod
    async def update_submitted_rating(cls, order_id: str, stars: int) -> dict[str, Any] | None:
        reviews = await cls.read_all()
        review_entry = await cls._ensure_review_entry(reviews, order_id)
        if review_entry is None:
            return None
        review_entry['submitted_stars'] = stars
        async with aiofiles.open(cls.FILE_PATH, mode='w') as file:
            await file.write(json.dumps(reviews, indent=1))
        return reviews[order_id]

    @classmethod
    async def read_restaurants(cls) -> dict[str, dict[str, Any]]:
        if not cls.RESTAURANTS_FILE_PATH.exists():
            return {}
        async with aiofiles.open(cls.RESTAURANTS_FILE_PATH, mode='r') as file:
            raw_restaurants = await file.read()
        if not raw_restaurants:
            return {}
        return json.loads(raw_restaurants)

    @classmethod
    async def read_reports(cls) -> list[dict[str, Any]]:
        if not cls.REPORTS_FILE_PATH.exists():
            return []
        async with aiofiles.open(cls.REPORTS_FILE_PATH, mode='r') as file:
            raw_reports = await file.read()
        if not raw_reports:
            return []
        return json.loads(raw_reports)

    @classmethod
    async def get_restaurant_id_by_order_id(cls, order_id: str) -> int | None:
        restaurants = await cls.read_restaurants()
        for restaurant_id, restaurant_data in restaurants.items():
            if order_id in restaurant_data.get('order_ids', []):
                return int(restaurant_id)
        return None

    @classmethod
    async def update_review_text(cls, order_id: str, review_text: str) -> dict[str, Any] | None:
        reviews = await cls.read_all()
        review_entry = await cls._ensure_review_entry(reviews, order_id)
        if review_entry is None:
            return None
        review_entry['review_text'] = review_text
        async with aiofiles.open(cls.FILE_PATH, mode='w') as file:
            await file.write(json.dumps(reviews, indent=1))
        return reviews[order_id]

    @classmethod
    async def update_review_fields(cls, order_id: str, stars: int | None=None, review_text: str | None=None) -> dict[str, Any] | None:
        reviews = await cls.read_all()
        review_entry = await cls._ensure_review_entry(reviews, order_id)
        if review_entry is None:
            return None
        if stars is not None:
            review_entry['submitted_stars'] = stars
        if review_text is not None:
            review_entry['review_text'] = review_text
        async with aiofiles.open(cls.FILE_PATH, mode='w') as file:
            await file.write(json.dumps(reviews, indent=1))
        return reviews[order_id]

    @classmethod
    async def delete_review(cls, order_id: str) -> dict[str, Any] | None:
        reviews = await cls.read_all()
        if order_id not in reviews:
            return None
        reviews[order_id]['submitted_stars'] = None
        reviews[order_id]['review_text'] = None
        async with aiofiles.open(cls.FILE_PATH, mode='w') as file:
            await file.write(json.dumps(reviews, indent=1))
        return reviews[order_id]

    @classmethod
    async def get_restaurant_reviews(cls, restaurant_id: int, stars: int | None=None) -> list[dict[str, Any]] | None:
        restaurants = await cls.read_restaurants()
        restaurant_data = restaurants.get(str(restaurant_id))
        if restaurant_data is None:
            return None
        order_ids = restaurant_data.get('order_ids', [])
        reviews = await cls.read_all()
        filtered_reviews = []
        for order_id in order_ids:
            order = reviews.get(order_id)
            if order is None:
                continue
            has_feedback = order.get('submitted_stars') is not None or order.get('review_text') is not None
            if not has_feedback:
                continue
            if stars is not None and order.get('submitted_stars') != stars:
                continue
            filtered_reviews.append({'order_id': order_id, 'submitted_stars': order.get('submitted_stars'), 'review_text': order.get('review_text')})
        return filtered_reviews

    @classmethod
    async def create_report(cls, order_id: str, reason: str, description: str | None=None) -> dict[str, Any]:
        reports = await cls.read_reports()
        report = {'report_id': len(reports) + 1, 'order_id': order_id, 'reason': reason, 'description': description}
        reports.append(report)
        async with aiofiles.open(cls.REPORTS_FILE_PATH, mode='w') as file:
            await file.write(json.dumps(reports, indent=1))
        return report
