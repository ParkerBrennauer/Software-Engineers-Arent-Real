import pytest
from src.schemas import UserRole
from src.repositories import UserRepo
from src.services import UserService


@pytest.mark.asyncio
async def test_reassign_user_as_driver_success(monkeypatch):
    target_user = {
        "id": 2,
        "username": "customer1",
        "role": UserRole.CUSTOMER,
        "email": "customer@example.com",
        "name": "Customer",
        "hashed_password": "h",
        "is_active": True,
        "requires_2fa": False,
    }
    captured = {}

    async def fake_get_by_username(username: str):
        if username == "customer1":
            return target_user
        return None

    async def fake_update_by_username(username: str, updates: dict):
        captured["username"] = username
        captured["updates"] = updates
        return {**target_user, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    updated = await UserService.reassign_user_as_driver("customer1")

    assert captured["username"] == "customer1"
    assert captured["updates"]["role"] == UserRole.DRIVER
    assert captured["updates"]["requires_2fa"] is True
    assert updated.role == UserRole.DRIVER


@pytest.mark.asyncio
async def test_reassign_user_as_driver_user_not_found(monkeypatch):
    async def fake_get_by_username(_username: str):
        return None

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="User not found"):
        await UserService.reassign_user_as_driver("missing")


@pytest.mark.asyncio
async def test_reassign_user_as_driver_blocks_owner(monkeypatch):
    owner_user = {
        "id": 1,
        "username": "owner1",
        "role": UserRole.RESTAURANT_OWNER,
        "email": "owner@example.com",
        "name": "Owner",
        "hashed_password": "h",
        "is_active": True,
        "requires_2fa": True,
        "restaurant_id": 1,
    }

    async def fake_get_by_username(_username: str):
        return owner_user

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="Cannot assign restaurant owner as driver"):
        await UserService.reassign_user_as_driver("owner1")


@pytest.mark.asyncio
async def test_reassign_user_as_driver_already_driver_is_idempotent(monkeypatch):
    driver_user = {
        "id": 3,
        "username": "driver1",
        "role": UserRole.DRIVER,
        "email": "driver@example.com",
        "name": "Driver",
        "hashed_password": "h",
        "is_active": True,
        "requires_2fa": True,
    }

    async def fake_get_by_username(_username: str):
        return driver_user

    async def fake_update_by_username(_username: str, _updates: dict):
        raise AssertionError("update_by_username should not be called for an existing driver")

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    updated = await UserService.reassign_user_as_driver("driver1")
    assert updated.role == UserRole.DRIVER
