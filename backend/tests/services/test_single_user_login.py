import pytest
from src.repositories.user_repo import UserRepo
from src.services.user_service import UserService


@pytest.fixture(autouse=True)
def reset_logged_in_user():
    UserService._current_logged_in_user = None
    yield
    UserService._current_logged_in_user = None


@pytest.mark.asyncio
async def test_single_user_login_enforcement(monkeypatch):
    user_data1 = {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com",
        "name": "User One",
        "role": "customer",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": True,
        "requires_2fa": False,
    }

    user_data2 = {
        "id": 2,
        "username": "user2",
        "email": "user2@example.com",
        "name": "User Two",
        "role": "customer",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuvwxyz",
        "is_active": True,
        "requires_2fa": False,
    }

    def fake_get_by_username(username: str):
        if username == "user1":
            return user_data1
        return user_data2

    async def async_fake_get_by_username(username: str):
        return fake_get_by_username(username)

    async def fake_verify_password(_plain: str, _hashed: str):
        return True

    async def fake_update_by_username(username: str, data: dict):
        return {"username": username, **data}

    monkeypatch.setattr(UserRepo, "get_by_username", async_fake_get_by_username)
    monkeypatch.setattr(UserService, "verify_password", fake_verify_password)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    user = await UserService.login_user("user1", "password123")
    assert user.username == "user1"
    assert UserService.get_current_user() == "user1"

    with pytest.raises(
        ValueError, match=r"Another user \(user1\) is already logged in."
    ):
        await UserService.login_user("user2", "password123")

    assert UserService.get_current_user() == "user1"


@pytest.mark.asyncio
async def test_logout_user(monkeypatch):
    UserService._current_logged_in_user = "user1"

    async def fake_update_by_username(username: str, data: dict):
        return True

    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    success = await UserService.logout_user("user1")
    assert success is True
    assert UserService.get_current_user() is None


@pytest.mark.asyncio
async def test_logout_wrong_user(monkeypatch):
    UserService._current_logged_in_user = "user1"

    async def fake_update_by_username(username: str, data: dict):
        return True

    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    success = await UserService.logout_user("user2")
    assert success is True
    assert UserService.get_current_user() == "user1"


@pytest.mark.asyncio
async def test_get_current_user_no_user():
    UserService._current_logged_in_user = None
    assert UserService.get_current_user() is None
