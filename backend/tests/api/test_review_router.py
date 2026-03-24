import httpx
import pytest

from src.main import app
from src.schemas.review_schema import (
    DeleteResponse,
    ReviewCreate,
    ReviewEdit,
    ReviewEditResponse,
    ReviewResponse,
)
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


@pytest.mark.asyncio
async def test_edit_review_success(monkeypatch):
    async def fake_edit_order_review(_order_id: str, _payload: ReviewEdit):
        return ReviewEditResponse(
            order_id="1d8e87M",
            submitted_stars=5,
            review_text="Updated review",
        )

    monkeypatch.setattr(RatingService, "edit_order_review", fake_edit_order_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            "/orders/1d8e87M/review",
            json={"stars": 5, "review_text": "Updated review"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1d8e87M",
        "submitted_stars": 5,
        "review_text": "Updated review",
    }


@pytest.mark.asyncio
async def test_edit_review_order_not_found(monkeypatch):
    async def fake_edit_order_review(_order_id: str, _payload: ReviewEdit):
        raise ValueError("Order not found")

    monkeypatch.setattr(RatingService, "edit_order_review", fake_edit_order_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            "/orders/FAKE_ID/review",
            json={"stars": 3},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_edit_review_no_existing_review(monkeypatch):
    async def fake_edit_order_review(_order_id: str, _payload: ReviewEdit):
        raise ValueError("No review exists to edit for this order")

    monkeypatch.setattr(RatingService, "edit_order_review", fake_edit_order_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            "/orders/1d8e87M/review",
            json={"stars": 3},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "No review exists to edit for this order"


@pytest.mark.asyncio
async def test_edit_review_nothing_to_update(monkeypatch):
    async def fake_edit_order_review(_order_id: str, _payload: ReviewEdit):
        raise ValueError("Nothing to update")

    monkeypatch.setattr(RatingService, "edit_order_review", fake_edit_order_review)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.put(
            "/orders/1d8e87M/review",
            json={},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Nothing to update"


@pytest.mark.asyncio
async def test_delete_review_success(monkeypatch):
    async def fake_delete_order_review(_order_id: str):
        return DeleteResponse(
            order_id="1d8e87M",
            message="Review and rating deleted successfully",
        )

    monkeypatch.setattr(
        RatingService,
        "delete_order_review",
        fake_delete_order_review,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.delete("/orders/1d8e87M/review")

    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1d8e87M",
        "message": "Review and rating deleted successfully",
    }


@pytest.mark.asyncio
async def test_delete_review_order_not_found(monkeypatch):
    async def fake_delete_order_review(_order_id: str):
        raise ValueError("Order not found")

    monkeypatch.setattr(
        RatingService,
        "delete_order_review",
        fake_delete_order_review,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.delete("/orders/FAKE_ID/review")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_delete_review_nothing_to_delete(monkeypatch):
    async def fake_delete_order_review(_order_id: str):
        raise ValueError("No review exists to delete for this order")

    monkeypatch.setattr(
        RatingService,
        "delete_order_review",
        fake_delete_order_review,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.delete("/orders/1d8e87M/review")

    assert response.status_code == 400
    assert response.json()["detail"] == "No review exists to delete for this order"
