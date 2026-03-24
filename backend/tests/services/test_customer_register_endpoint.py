import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repositories.user_repo import UserRepo
from src.services.user_service import UserService


client = TestClient(app)


@pytest.mark.asyncio
async def test_register_customer_endpoint_success():
    """Test successful customer registration via endpoint"""
    
    async def fake_get_by_username(_username: str):
        return None

    async def fake_get_password_hash(_password: str):
        return "hashed_pw"

    async def fake_save_user(user_data: dict):
        return {"id": 1, **user_data}

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "get_password_hash", fake_get_password_hash)
    monkeypatch.setattr(UserRepo, "save_user", fake_save_user)

    response = client.post(
        "/users/register/customer",
        json={
            "email": "test@example.com",
            "name": "Test Customer",
            "username": "testcust1",
            "password": "secret123",
            "payment_type": "credit card",
            "payment_details": "1234567812345678",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "testcust1"
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_register_customer_endpoint_duplicate_username():
    """Test customer registration with duplicate username"""
    
    async def fake_get_by_username(_username: str):
        return {"id": 10, "username": "taken"}

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    response = client.post(
        "/users/register/customer",
        json={
            "email": "dup@example.com",
            "name": "Dup Customer",
            "username": "taken",
            "password": "secret123",
            "payment_type": "credit card",
            "payment_details": "1234567812345678",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_register_customer_endpoint_invalid_card():
    """Test customer registration with invalid card format"""
    
    response = client.post(
        "/users/register/customer",
        json={
            "email": "test@example.com",
            "name": "Test Customer",
            "username": "testcust2",
            "password": "secret123",
            "payment_type": "credit card",
            "payment_details": "abcd",
        },
    )

    assert response.status_code == 422
    assert "Card number must contain only digits" in str(response.json())


@pytest.mark.asyncio
async def test_register_customer_endpoint_invalid_payment_type():
    """Test customer registration with invalid payment type"""
    
    response = client.post(
        "/users/register/customer",
        json={
            "email": "test@example.com",
            "name": "Test Customer",
            "username": "testcust3",
            "password": "secret123",
            "payment_type": "bitcoin",
            "payment_details": "1234567812345678",
        },
    )

    assert response.status_code == 422
    assert "Payment type must be either credit card or debit card" in str(response.json())
