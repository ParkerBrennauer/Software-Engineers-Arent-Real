import httpx
import pytest

from src.main import app
from src.schemas.review_schema import ReviewCreate, ReviewResponse
from src.services.rating_service import RatingService


@pytest.mark.asyncio
async def test_review_order_success(monkeypatch):
    async def fake_submit_review(_order_id: str, _payload: ReviewCreate):
        return ReviewResponse(
            order_id="1d8e87M",
            restaurant_id=16,
            review_text="Great food, fast delivery!",
        )

    monkeypatch.setattr(RatingService, "submit_review", fake_submit_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review",
            json={"review_text": "Great food, fast delivery!"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1d8e87M",
        "restaurant_id": 16,
        "review_text": "Great food, fast delivery!",
    }


@pytest.mark.asyncio
async def test_review_nonexistent_order(monkeypatch):
    async def fake_submit_review(_order_id: str, _payload: ReviewCreate):
        raise ValueError("Order not found")

    monkeypatch.setattr(RatingService, "submit_review", fake_submit_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/orders/NONEXISTENT_ORDER/review",
            json={"review_text": "Great food!"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_review_order_duplicate(monkeypatch):
    async def fake_submit_review(_order_id: str, _payload: ReviewCreate):
        raise ValueError("This order has already been reviewed")

    monkeypatch.setattr(RatingService, "submit_review", fake_submit_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review",
            json={"review_text": "Trying again"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "This order has already been reviewed"


@pytest.mark.asyncio
async def test_review_restaurant_not_found(monkeypatch):
    async def fake_submit_review(_order_id: str, _payload: ReviewCreate):
        raise ValueError("Restaurant not found for this order")

    monkeypatch.setattr(RatingService, "submit_review", fake_submit_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review",
            json={"review_text": "Great food!"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found for this order"


@pytest.mark.asyncio
async def test_review_order_invalid_text():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review",
            json={"review_text": ""},
        )

    assert response.status_code == 422
