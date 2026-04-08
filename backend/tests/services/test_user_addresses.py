import pytest
from src.repositories import UserRepo
from src.services import UserService
from src.schemas import UserRole

@pytest.mark.asyncio
async def test_add_address_success():
    username = 'test_user'
    new_address = '123 Test St'
    saved_addresses = ['000 Old St']

    async def fake_get_by_username(_username: str):
        return {'id': 1, 'username': _username, 'email': 'test@example.com', 'name': 'Test', 'role': UserRole.CUSTOMER, 'hashed_password': 'pw', 'saved_addresses': saved_addresses.copy()}

    async def fake_update_by_username(_username: str, updates: dict):
        return {'id': 1, 'username': _username, 'email': 'test@example.com', 'name': 'Test', 'role': UserRole.CUSTOMER, 'hashed_password': 'pw', 'saved_addresses': updates['saved_addresses']}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserRepo, 'update_by_username', fake_update_by_username)
    updated_user = await UserService.add_address(username, new_address)
    assert new_address in updated_user.saved_addresses
    assert '000 Old St' in updated_user.saved_addresses
    assert len(updated_user.saved_addresses) == 2
    monkeypatch.undo()

@pytest.mark.asyncio
async def test_add_address_duplicate():
    username = 'test_user'
    existing_address = '123 Test St'

    async def fake_get_by_username(_username: str):
        return {'id': 1, 'username': _username, 'email': 'test@example.com', 'name': 'Test', 'role': UserRole.CUSTOMER, 'hashed_password': 'pw', 'saved_addresses': [existing_address]}

    async def fake_update_by_username(_username: str, updates: dict):
        return {'id': 1, 'username': _username, 'email': 'test@example.com', 'name': 'Test', 'role': UserRole.CUSTOMER, 'hashed_password': 'pw', 'saved_addresses': updates['saved_addresses']}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserRepo, 'update_by_username', fake_update_by_username)
    updated_user = await UserService.add_address(username, existing_address)
    assert len(updated_user.saved_addresses) == 1
    assert updated_user.saved_addresses[0] == existing_address
    monkeypatch.undo()

@pytest.mark.asyncio
async def test_add_address_user_not_found():

    async def fake_get_by_username(_username: str):
        return None
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='User not found'):
        await UserService.add_address('non_existent', '123 Test St')
    monkeypatch.undo()

@pytest.mark.asyncio
async def test_get_addresses_success():
    username = 'test_user'
    saved_addresses = ['123 Test St', '456 Main St']

    async def fake_get_by_username(_username: str):
        return {'id': 1, 'username': _username, 'email': 'test@example.com', 'name': 'Test', 'role': UserRole.CUSTOMER, 'hashed_password': 'pw', 'saved_addresses': saved_addresses}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    addresses = await UserService.get_addresses(username)
    assert addresses == saved_addresses
    monkeypatch.undo()

@pytest.mark.asyncio
async def test_get_addresses_user_not_found():

    async def fake_get_by_username(_username: str):
        return None
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='User not found'):
        await UserService.get_addresses('non_existent')
    monkeypatch.undo()
