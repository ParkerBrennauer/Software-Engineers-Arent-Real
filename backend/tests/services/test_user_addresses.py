import pytest
from src.repositories import UserRepo
from src.services import UserService
from src.schemas.user_schema import UserRole, AddressAdd


@pytest.mark.asyncio
async def test_add_address_success():
    username = "test_user"
    new_address = "123 Test St"
    saved_addresses = ["000 Old St"]

    async def fake_get_by_username(_username: str):
        return {
            "id": 1,
            "username": _username,
            "email": "test@example.com",
            "name": "Test",
            "role": UserRole.CUSTOMER,
            "hashed_password": "pw",
            "saved_addresses": saved_addresses.copy(),
        }

    async def fake_update_by_username(_username: str, updates: dict):
        return {
            "id": 1,
            "username": _username,
            "email": "test@example.com",
            "name": "Test",
            "role": UserRole.CUSTOMER,
            "hashed_password": "pw",
            "saved_addresses": updates["saved_addresses"],
        }

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)
    updated_user = await UserService.add_address(
        username, AddressAdd(address=new_address, latitude=0.0, longitude=0.0)
    )
    assert new_address in updated_user.saved_addresses
    assert "000 Old St" in updated_user.saved_addresses
    assert len(updated_user.saved_addresses) == 2
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_add_address_duplicate():
    username = "test_user"
    existing_address = "123 Test St"

    async def fake_get_by_username(_username: str):
        return {
            "id": 1,
            "username": _username,
            "email": "test@example.com",
            "name": "Test",
            "role": UserRole.CUSTOMER,
            "hashed_password": "pw",
            "saved_addresses": [existing_address],
        }

    async def fake_update_by_username(_username: str, updates: dict):
        return {
            "id": 1,
            "username": _username,
            "email": "test@example.com",
            "name": "Test",
            "role": UserRole.CUSTOMER,
            "hashed_password": "pw",
            "saved_addresses": updates["saved_addresses"],
        }

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(UserRepo, "update_by_username", fake_update_by_username)
    updated_user = await UserService.add_address(
        username, AddressAdd(address=existing_address, latitude=0.0, longitude=0.0)
    )
    assert len(updated_user.saved_addresses) == 1
    assert updated_user.saved_addresses[0] == existing_address
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_add_address_user_not_found():

    async def fake_get_by_username(_username: str):
        return None

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    with pytest.raises(ValueError, match="User not found"):
        await UserService.add_address(
            "non_existent",
            AddressAdd(address="123 Test St", latitude=0.0, longitude=0.0),
        )
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_get_addresses_success():
    username = "test_user"
    saved_addresses = ["123 Test St", "456 Main St"]
    locations = [[-119.0, 49.0], [-119.5, 49.5]]

    async def fake_get_by_username(_username: str):
        return {
            "id": 1,
            "username": _username,
            "email": "test@example.com",
            "name": "Test",
            "role": UserRole.CUSTOMER,
            "hashed_password": "pw",
            "saved_addresses": saved_addresses,
            "location": locations,
        }

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    addresses = await UserService.get_addresses(username)
    assert len(addresses) == 2
    assert addresses[0].address == "123 Test St"
    assert addresses[0].longitude == -119.0
    assert addresses[1].address == "456 Main St"
    assert addresses[1].latitude == 49.5
    monkeypatch.undo()


@pytest.mark.asyncio
async def test_get_addresses_user_not_found():

    async def fake_get_by_username(_username: str):
        return None

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    with pytest.raises(ValueError, match="User not found"):
        await UserService.get_addresses("non_existent")
    monkeypatch.undo()
