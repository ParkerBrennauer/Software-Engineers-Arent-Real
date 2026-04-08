import httpx
import pytest
from src.main import app
from src.schemas.rating_schema import RatingCreate, RatingResponse
from src.services.rating_service import RatingService
from src.services.user_service import UserService
from src.repositories.rating_repo import RatingRepo


@pytest.mark.asyncio
async def test_rate_order_success(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_submit_rating(_order_id: str, _payload: RatingCreate):
        return RatingResponse(order_id="1d8e87M", stars=5)

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "submit_rating", fake_submit_rating)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/1d8e87M/rating", json={"stars": 5})
    assert response.status_code == 200
    assert response.json() == {"order_id": "1d8e87M", "stars": 5}


@pytest.mark.asyncio
async def test_rate_nonexistent_order(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/NONEXISTENT_ORDER/rating", json={"stars": 3}
        )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_rate_order_duplicate(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_submit_rating(_order_id: str, _payload: RatingCreate):
        raise ValueError("This order has already been rated")

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "submit_rating", fake_submit_rating)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/f4d84dC/rating", json={"stars": 2})
    assert response.status_code == 400
    assert response.json()["detail"] == "This order has already been rated"


@pytest.mark.asyncio
async def test_rate_order_invalid_stars_zero():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/1d8e87M/rating", json={"stars": 0})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rate_order_invalid_stars_six():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/1d8e87M/rating", json={"stars": 6})
    assert response.status_code == 422
