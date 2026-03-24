from datetime import datetime, timedelta, timezone
import pytest
from src.repositories.user_repo import UserRepo
from src.services.user_service import UserService


@pytest.mark.asyncio
async def test_reset_password_success(monkeypatch):
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    user_data = {
        "id": 1,
        "username": "user1",
        "two_factor_code": "123456",
        "two_factor_expires_at": expires,
        "hashed_password": "old_hash",
    }
    captured = {}

    async def fake_get_by_username(_username: str):
        return dict(user_data)

    async def fake_get_password_hash(_password: str):
        return "new_hash"

    async def fake_update_by_username(_username: str, updates: dict):
        captured.update(updates)
        return {**user_data, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "get_password_hash", fake_get_password_hash)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    result = await UserService.reset_password("user1", "123456", "newpassword")

    assert result is True
    assert captured["hashed_password"] == "new_hash"


@pytest.mark.asyncio
async def test_reset_password_user_not_found(monkeypatch):
    async def fake_get_by_username(_username: str):
        return None

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="User not found"):
        await UserService.reset_password("ghost", "123456", "newpassword")


@pytest.mark.asyncio
async def test_reset_password_invalid_code(monkeypatch):
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    user_data = {
        "id": 1,
        "username": "user1",
        "two_factor_code": "123456",
        "two_factor_expires_at": expires,
    }

    async def fake_get_by_username(_username: str):
        return dict(user_data)

    async def fake_update_by_username(_username: str, updates: dict):
        return {**user_data, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    with pytest.raises(ValueError, match="Invalid 2FA code"):
        await UserService.reset_password("user1", "000000", "newpassword")


@pytest.mark.asyncio
async def test_reset_password_expired_code(monkeypatch):
    expires = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    user_data = {
        "id": 1,
        "username": "user1",
        "two_factor_code": "123456",
        "two_factor_expires_at": expires,
    }

    async def fake_get_by_username(_username: str):
        return dict(user_data)

    async def fake_update_by_username(_username: str, updates: dict):
        return {**user_data, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    with pytest.raises(ValueError, match="2FA code has expired"):
        await UserService.reset_password("user1", "123456", "newpassword")


@pytest.mark.asyncio
async def test_reset_password_no_code_generated(monkeypatch):
    user_data = {
        "id": 1,
        "username": "user1",
        "two_factor_code": None,
        "two_factor_expires_at": None,
    }

    async def fake_get_by_username(_username: str):
        return dict(user_data)

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="No 2FA code has been generated"):
        await UserService.reset_password("user1", "123456", "newpassword")
