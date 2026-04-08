import pytest
from src.repositories.user_repo import UserRepo
from src.services.user_service import UserService


@pytest.fixture(autouse=True)
def reset_logged_in_user():
    UserService._current_logged_in_user = None
    yield
    UserService._current_logged_in_user = None


@pytest.mark.asyncio
async def test_login_user_success_driver(monkeypatch):
    user_data = {
        "id": 1,
        "username": "driver1",
        "email": "driver@example.com",
        "name": "John Driver",
        "role": "driver",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": True,
        "requires_2fa": True,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_verify_password(_plain: str, _hashed: str):
        return True

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)

    user = await UserService.login_user("driver1", "password123")

    assert user.id == 1
    assert user.username == "driver1"
    assert user.requires_2fa is True


@pytest.mark.asyncio
async def test_login_user_success_customer(monkeypatch):
    user_data = {
        "id": 2,
        "username": "customer1",
        "email": "customer@example.com",
        "name": "Jane Customer",
        "role": "customer",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": True,
        "requires_2fa": False,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_verify_password(_plain: str, _hashed: str):
        return True

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)

    user = await UserService.login_user("customer1", "password123")

    assert user.id == 2
    assert user.username == "customer1"
    assert user.requires_2fa is False


@pytest.mark.asyncio
async def test_login_user_success_restaurant_owner(monkeypatch):
    user_data = {
        "id": 3,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Bob Owner",
        "role": "owner",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": True,
        "requires_2fa": True,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_verify_password(_plain: str, _hashed: str):
        return True

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)

    user = await UserService.login_user("owner1", "password123")

    assert user.id == 3
    assert user.requires_2fa is True


@pytest.mark.asyncio
async def test_login_user_success_restaurant_staff(monkeypatch):
    user_data = {
        "id": 4,
        "username": "staff1",
        "email": "staff@example.com",
        "name": "Alice Staff",
        "role": "staff",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": True,
        "requires_2fa": True,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_verify_password(_plain: str, _hashed: str):
        return True

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)

    user = await UserService.login_user("staff1", "password123")

    assert user.id == 4
    assert user.requires_2fa is True


@pytest.mark.asyncio
async def test_login_user_not_found(monkeypatch):

    async def fake_get_by_username(_username: str):
        return None

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="Invalid username or password"):
        await UserService.login_user("nonexistent", "password123")


@pytest.mark.asyncio
async def test_login_user_invalid_password(monkeypatch):
    user_data = {
        "id": 1,
        "username": "driver1",
        "email": "driver@example.com",
        "name": "John Driver",
        "role": "driver",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": True,
        "requires_2fa": True,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_verify_password(_plain: str, _hashed: str):
        return False

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)

    with pytest.raises(ValueError, match="Invalid username or password"):
        await UserService.login_user("driver1", "wrongpassword")


@pytest.mark.asyncio
async def test_login_user_inactive_account(monkeypatch):
    user_data = {
        "id": 1,
        "username": "driver1",
        "email": "driver@example.com",
        "name": "John Driver",
        "role": "driver",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": False,
        "requires_2fa": True,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_verify_password(_plain: str, _hashed: str):
        return True

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)

    with pytest.raises(ValueError, match="User account is inactive"):
        await UserService.login_user("driver1", "password123")


@pytest.mark.asyncio
async def test_login_user_missing_hashed_password(monkeypatch):
    user_data = {
        "id": 1,
        "username": "driver1",
        "email": "driver@example.com",
        "name": "John Driver",
        "role": "driver",
        "is_active": True,
        "requires_2fa": True,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_verify_password(_plain: str, _hashed: str):
        return False

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)

    with pytest.raises(ValueError, match="Invalid username or password"):
        await UserService.login_user("driver1", "password123")
