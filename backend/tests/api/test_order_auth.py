import httpx
import pytest
from src.main import app
from src.schemas.order_schema import OrderCreate, OrderUpdate
from src.models.order_model import OrderInternal
from src.services.order_services import OrderService
from src.services.user_service import UserService
from src.repositories.order_repo import OrderRepo


@pytest.mark.asyncio
async def test_place_order_success(monkeypatch):
    def fake_get_current_user():
        return "customer1"

    async def fake_create_order(_order: OrderCreate):
        return OrderInternal(
            id="1",
            items=_order.items,
            cost=_order.cost,
            restaurant=_order.restaurant,
            customer="customer1",
            time=_order.time,
            cuisine=_order.cuisine,
            distance=_order.distance or 0.0,
            order_status="created",
            payment_status="pending",
        )

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderService, "create_order", fake_create_order)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/place",
            json={
                "items": ["burger", "fries"],
                "cost": 15.99,
                "restaurant": "McDonald's",
                "customer": "wrong_customer",
                "time": 1234567890,
                "cuisine": "Fast Food",
                "distance": 2.5,
            },
        )

    assert response.status_code == 201
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_place_order_not_logged_in(monkeypatch):
    def fake_get_current_user():
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/place",
            json={
                "items": ["burger"],
                "cost": 10.0,
                "restaurant": "McDonald's",
                "customer": "customer1",
                "time": 1234567890,
                "cuisine": "Fast Food",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "No user currently logged in"


@pytest.mark.asyncio
async def test_add_items_to_order_success(monkeypatch):
    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_id(_order_id):
        return {"id": _order_id, "customer": "customer1", "items": ["burger"]}

    async def fake_update_order(_order_id, _update_data):
        return OrderInternal(
            id=str(_order_id),
            items=_update_data["items"],
            cost=10.0,
            restaurant="McDonald's",
            customer="customer1",
            time=1234567890,
            cuisine="Fast Food",
            distance=2.5,
            order_status="created",
            payment_status="pending",
        )

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderService, "update_order", fake_update_order)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/1/items",
            json={"items": ["burger", "fries", "drink"]},
        )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 3


@pytest.mark.asyncio
async def test_add_items_to_order_not_logged_in(monkeypatch):
    def fake_get_current_user():
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/1/items",
            json={"items": ["burger"]},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "No user currently logged in"


@pytest.mark.asyncio
async def test_add_items_to_order_not_found(monkeypatch):
    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_id(_order_id):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/999/items",
            json={"items": ["burger"]},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_add_items_to_order_permission_denied(monkeypatch):
    def fake_get_current_user():
        return "customer2"

    async def fake_get_by_id(_order_id):
        return {"id": _order_id, "customer": "customer1", "items": ["burger"]}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/1/items",
            json={"items": ["pizza"]},
        )

    assert response.status_code == 403
    assert "does not have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_order_status_success(monkeypatch):
    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_id(_order_id):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_get_order_status(_order_id):
        return {"id": _order_id, "status": "preparing"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderService, "get_order_status", fake_get_order_status)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/1")

    assert response.status_code == 200
    assert response.json()["status"] == "preparing"


@pytest.mark.asyncio
async def test_get_order_status_not_logged_in(monkeypatch):
    def fake_get_current_user():
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/1")

    assert response.status_code == 400
    assert response.json()["detail"] == "No user currently logged in"


@pytest.mark.asyncio
async def test_get_order_status_order_not_found(monkeypatch):
    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_id(_order_id):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_get_order_status_permission_denied(monkeypatch):
    def fake_get_current_user():
        return "customer2"

    async def fake_get_by_id(_order_id):
        return {"id": _order_id, "customer": "customer1"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/1")

    assert response.status_code == 403
    assert "does not have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_cancel_order_success(monkeypatch):
    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_id(_order_id):
        return {"id": _order_id, "customer": "customer1", "order_status": "created"}

    async def fake_cancel_order(_order_id):
        return {"id": _order_id, "order_status": "cancelled"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderService, "cancel_order", fake_cancel_order)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/1/cancel")

    assert response.status_code == 200
    assert response.json()["order_status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_order_not_logged_in(monkeypatch):
    def fake_get_current_user():
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/1/cancel")

    assert response.status_code == 400
    assert response.json()["detail"] == "No user currently logged in"


@pytest.mark.asyncio
async def test_cancel_order_not_found(monkeypatch):
    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_id(_order_id):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/999/cancel")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_cancel_order_permission_denied(monkeypatch):
    def fake_get_current_user():
        return "customer2"

    async def fake_get_by_id(_order_id):
        return {"id": _order_id, "customer": "customer1", "order_status": "created"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/1/cancel")

    assert response.status_code == 403
    assert "does not have permission" in response.json()["detail"]
