import pytest
from src.schemas.customer_schema import CustomerRegister
from src.schemas.user_schema import UserRole
from src.repositories import UserRepo
from src.services import UserService
from pydantic import ValidationError


@pytest.mark.asyncio
async def test_create_customer_success():
    customer_in = CustomerRegister(
        email="customer@example.com",
        name="John Customer",
        role=UserRole.CUSTOMER,
        username="johncust1",
        password="secret123",
        payment_type="credit card",
        payment_details="1234567812345678",
    )

    captured = {}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_get_password_hash(_password: str):
        return "hashed_pw"

    async def fake_save_user(user_data: dict):
        captured["payload"] = user_data
        return {"id": 1, **user_data}

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "get_password_hash", fake_get_password_hash)
    monkeypatch.setattr(UserRepo, "save_user", fake_save_user)

    created = await UserService.create_user(customer_in)

    assert created.id == 1
    assert created.username == "johncust1"
    payload = captured["payload"]
    assert payload["hashed_password"] == "hashed_pw"
    assert payload["requires_2fa"] is False
    assert payload["is_active"] is True
    assert payload["payment_type"] == "credit card"
    assert payload["payment_details"] == "1234567812345678"
    assert "password" not in payload
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_create_customer_invalid_card_non_digits():
    with pytest.raises(ValidationError) as exc_info:
        CustomerRegister(
            email="customer@example.com",
            name="John Customer",
            role=UserRole.CUSTOMER,
            username="johncust2",
            password="secret123",
            payment_type="credit card",
            payment_details="abcd1234efgh5678",
        )

    assert "Card number must contain only digits" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_customer_invalid_card_length():
    with pytest.raises(ValidationError) as exc_info:
        CustomerRegister(
            email="customer@example.com",
            name="John Customer",
            role=UserRole.CUSTOMER,
            username="johncust3",
            password="secret123",
            payment_type="credit card",
            payment_details="123456",
        )

    assert "Card number must be 15 or 16 digits" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_customer_invalid_payment_type():
    with pytest.raises(ValidationError) as exc_info:
        CustomerRegister(
            email="customer@example.com",
            name="John Customer",
            role=UserRole.CUSTOMER,
            username="johncust4",
            password="secret123",
            payment_type="paypal",
            payment_details="1234567812345678",
        )

    assert "Payment type must be either credit card or debit card" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_create_customer_duplicate_username_raises():
    customer_in = CustomerRegister(
        email="customer@example.com",
        name="John Customer",
        role=UserRole.CUSTOMER,
        username="taken",
        password="secret123",
        payment_type="credit card",
        payment_details="1234567812345678",
    )

    async def fake_get_by_username(_username: str):
        return {"id": 10, "username": "taken"}

    async def fake_save_user(user_data: dict):
        raise AssertionError("save_user should not be called")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "save_user", fake_save_user)

    with pytest.raises(ValueError, match="Username already exists"):
        await UserService.create_user(customer_in)

    monkeypatch.undo()


@pytest.mark.asyncio
async def test_create_customer_debit_card():
    customer_in = CustomerRegister(
        email="customer@example.com",
        name="Jane Customer",
        role=UserRole.CUSTOMER,
        username="janecust1",
        password="secret123",
        payment_type="debit card",
        payment_details="9876543210123456",
    )

    captured = {}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_get_password_hash(_password: str):
        return "hashed_pw"

    async def fake_save_user(user_data: dict):
        captured["payload"] = user_data
        return {"id": 2, **user_data}

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "get_password_hash", fake_get_password_hash)
    monkeypatch.setattr(UserRepo, "save_user", fake_save_user)

    created = await UserService.create_user(customer_in)

    assert created.id == 2
    payload = captured["payload"]
    assert payload["payment_type"] == "debit card"
    assert payload["payment_details"] == "9876543210123456"
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_create_customer_15_digit_card():
    customer_in = CustomerRegister(
        email="customer@example.com",
        name="Alex Customer",
        role=UserRole.CUSTOMER,
        username="alexcust1",
        password="secret123",
        payment_type="credit card",
        payment_details="123456789012345",
    )

    captured = {}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_get_password_hash(_password: str):
        return "hashed_pw"

    async def fake_save_user(user_data: dict):
        captured["payload"] = user_data
        return {"id": 3, **user_data}

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "get_password_hash", fake_get_password_hash)
    monkeypatch.setattr(UserRepo, "save_user", fake_save_user)

    created = await UserService.create_user(customer_in)

    assert created.id == 3
    payload = captured["payload"]
    assert payload["payment_details"] == "123456789012345"
    monkeypatch.undo()
