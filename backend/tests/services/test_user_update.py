import pytest
from src.repositories import UserRepo
from src.services import UserService
from src.schemas import UserRole, UserUpdate


@pytest.mark.asyncio
async def test_update_user_success_password_and_role(monkeypatch):
    user_in = UserUpdate(password="new_secret", role=UserRole.DRIVER, name="New Name")
    captured = {}

    existing_user = {
        "id": 7,
        "email": "u@example.com",
        "name": "Old Name",
        "role": UserRole.CUSTOMER,
        "username": "user7",
        "hashed_password": "old_hash",
        "is_active": True,
        "requires_2fa": False,
    }

    async def fake_get_by_username(username: str):
        if username == "user7":
            return existing_user
        return None

    async def fake_get_password_hash(_password: str):
        return "new_hash"

    async def fake_update_by_username(username: str, updates: dict):
        captured["username"] = username
        captured["updates"] = updates
        return {**existing_user, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserService, "get_password_hash", fake_get_password_hash)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    updated = await UserService.update_user("user7", user_in)

    assert captured["username"] == "user7"
    assert "password" not in captured["updates"]
    assert captured["updates"]["hashed_password"] == "new_hash"
    assert captured["updates"]["requires_2fa"] is True
    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_update_user_duplicate_username_raises(monkeypatch):
    user_in = UserUpdate(username="taken")

    async def fake_get_by_username(username: str):
        if username == "current":
            return {
                "id": 1,
                "username": "current",
                "name": "Current",
                "email": "c@example.com",
                "role": UserRole.CUSTOMER,
                "hashed_password": "h",
                "is_active": True,
            }
        if username == "taken":
            return {"id": 2, "username": "taken"}
        return None

    async def fake_update_by_username(_username: str, _updates: dict):
        raise AssertionError("update_by_username should not be called")

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    with pytest.raises(ValueError, match="Username already exists"):
        await UserService.update_user("current", user_in)
