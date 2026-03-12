import pytest
from datetime import datetime, timedelta, timezone
from src.schemas.user_schema import UserRegister, UserRole, UserUpdate
from src.services.user_service import UserService
from src.repositories.user_repo import UserRepo


@pytest.mark.asyncio
async def test_create_user_success_customer():
    user_in = UserRegister(
        email="c@example.com",
        name="Cust User",
        role=UserRole.CUSTOMER,
        username="cust1",
        password="secret123",
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

    created = await UserService.create_user(user_in)

    assert created.id == 1
    assert created.username == "cust1"
    payload = captured["payload"]
    assert payload["hashed_password"] == "hashed_pw"
    assert payload["requires_2fa"] is False
    assert payload["is_active"] is True
    assert "password" not in payload
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_create_user_duplicate_username_raises():
    user_in = UserRegister(
        email="dup@example.com",
        name="Dup User",
        role=UserRole.CUSTOMER,
        username="taken",
        password="secret123",
    )

    async def fake_get_by_username(_username: str):
        return {"id": 10, "username": "taken"}

    async def fake_save_user(user_data: dict):
        raise AssertionError("save_user should not be called")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "save_user", fake_save_user)

    with pytest.raises(ValueError, match="Username already exists"):
        await UserService.create_user(user_in)

    monkeypatch.undo()


@pytest.mark.asyncio
async def test_create_user_driver_requires_2fa():
    user_in = UserRegister(
        email="d@example.com",
        name="Driver User",
        role=UserRole.DRIVER,
        username="driver1",
        password="secret123",
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

    await UserService.create_user(user_in)
    payload = captured["payload"]
    assert payload["requires_2fa"] is True
    monkeypatch.undo()


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


@pytest.mark.asyncio
async def test_generate_2fa_code_success(monkeypatch):
    user_data = {
        "id": 1,
        "username": "driver1",
        "email": "d@example.com",
        "name": "Driver",
        "role": "driver",
        "hashed_password": "h",
        "is_active": True,
        "requires_2fa": True,
    }
    captured = {}

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_update_by_username(_username: str, updates: dict):
        captured["updates"] = updates
        return {**user_data, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    code = await UserService.generate_2fa_code("driver1")

    assert len(code) == 6
    assert code.isdigit()
    assert captured["updates"]["two_factor_code"] == code
    assert captured["updates"]["two_factor_expires_at"] is not None


@pytest.mark.asyncio
async def test_generate_2fa_code_user_not_found(monkeypatch):
    async def fake_get_by_username(_username: str):
        return None

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="User not found"):
        await UserService.generate_2fa_code("nouser")


@pytest.mark.asyncio
async def test_generate_2fa_code_not_required(monkeypatch):
    user_data = {
        "id": 1,
        "username": "cust1",
        "requires_2fa": False,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="2FA is not required for this user"):
        await UserService.generate_2fa_code("cust1")


@pytest.mark.asyncio
async def test_verify_2fa_code_success(monkeypatch):
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    user_data = {
        "id": 1,
        "username": "driver1",
        "two_factor_code": "123456",
        "two_factor_expires_at": expires,
    }
    captured = {}

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_update_by_username(_username: str, updates: dict):
        captured["updates"] = updates
        return {**user_data, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    result = await UserService.verify_2fa_code("driver1", "123456")

    assert result is True
    assert captured["updates"]["two_factor_code"] is None
    assert captured["updates"]["two_factor_expires_at"] is None


@pytest.mark.asyncio
async def test_verify_2fa_code_invalid(monkeypatch):
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    user_data = {
        "id": 1,
        "username": "driver1",
        "two_factor_code": "123456",
        "two_factor_expires_at": expires,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="Invalid 2FA code"):
        await UserService.verify_2fa_code("driver1", "000000")


@pytest.mark.asyncio
async def test_verify_2fa_code_expired(monkeypatch):
    expires = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    user_data = {
        "id": 1,
        "username": "driver1",
        "two_factor_code": "123456",
        "two_factor_expires_at": expires,
    }
    captured = {}

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_update_by_username(_username: str, updates: dict):
        captured["updates"] = updates
        return {**user_data, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)

    with pytest.raises(ValueError, match="2FA code has expired"):
        await UserService.verify_2fa_code("driver1", "123456")


@pytest.mark.asyncio
async def test_verify_2fa_code_no_code_generated(monkeypatch):
    user_data = {
        "id": 1,
        "username": "driver1",
        "two_factor_code": None,
        "two_factor_expires_at": None,
    }

    async def fake_get_by_username(_username: str):
        return user_data

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)

    with pytest.raises(ValueError, match="No 2FA code has been generated"):
        await UserService.verify_2fa_code("driver1", "123456")
