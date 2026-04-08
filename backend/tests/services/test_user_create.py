import pytest
from src.schemas import UserRegister, UserRole
from src.repositories import UserRepo
from src.services import UserService

@pytest.mark.asyncio
async def test_create_user_success_customer():
    user_in = UserRegister(email='c@example.com', name='Cust User', role=UserRole.CUSTOMER, username='cust1', password='secret123')
    captured = {}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_get_password_hash(_password: str):
        return 'hashed_pw'

    async def fake_save_user(user_data: dict):
        captured['payload'] = user_data
        return {'id': 1, **user_data}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserService, 'get_password_hash', fake_get_password_hash)
    monkeypatch.setattr(UserRepo, 'save_user', fake_save_user)
    created = await UserService.create_user(user_in)
    assert created.id == 1
    assert created.username == 'cust1'
    payload = captured['payload']
    assert payload['hashed_password'] == 'hashed_pw'
    assert payload['requires_2fa'] is False
    assert payload['is_active'] is True
    assert 'password' not in payload
    monkeypatch.undo()

@pytest.mark.asyncio
async def test_create_user_duplicate_username_raises():
    user_in = UserRegister(email='dup@example.com', name='Dup User', role=UserRole.CUSTOMER, username='taken', password='secret123')

    async def fake_get_by_username(_username: str):
        return {'id': 10, 'username': 'taken'}

    async def fake_save_user(user_data: dict):
        raise AssertionError('save_user should not be called')
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserRepo, 'save_user', fake_save_user)
    with pytest.raises(ValueError, match='Username already exists'):
        await UserService.create_user(user_in)
    monkeypatch.undo()

@pytest.mark.asyncio
async def test_create_user_driver_requires_2fa():
    user_in = UserRegister(email='d@example.com', name='Driver User', role=UserRole.DRIVER, username='driver1', password='secret123')
    captured = {}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_get_password_hash(_password: str):
        return 'hashed_pw'

    async def fake_save_user(user_data: dict):
        captured['payload'] = user_data
        return {'id': 2, **user_data}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserService, 'get_password_hash', fake_get_password_hash)
    monkeypatch.setattr(UserRepo, 'save_user', fake_save_user)
    await UserService.create_user(user_in)
    payload = captured['payload']
    assert payload['requires_2fa'] is True
    monkeypatch.undo()
