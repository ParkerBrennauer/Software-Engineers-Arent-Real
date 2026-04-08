import pytest
from src.schemas import UserRole
from src.schemas.driver_schema import DriverRegister
from src.repositories import UserRepo
from src.services import UserService

@pytest.mark.asyncio
async def test_register_driver_success(monkeypatch):
    driver_in = DriverRegister(email='driver@example.com', name='John Driver', username='driver1', password='secret123')
    captured = {}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_get_password_hash(_password: str):
        return 'hashed_pw'

    async def fake_save_user(user_data: dict):
        captured['payload'] = user_data
        return {'id': 2, **user_data}
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserService, 'get_password_hash', fake_get_password_hash)
    monkeypatch.setattr(UserRepo, 'save_user', fake_save_user)
    created = await UserService.create_user(driver_in)
    assert created.role == UserRole.DRIVER
    assert created.username == 'driver1'
    payload = captured['payload']
    assert payload['role'] == UserRole.DRIVER
    assert payload['hashed_password'] == 'hashed_pw'
    assert payload['requires_2fa'] is True
    assert payload['is_active'] is True
    assert 'password' not in payload

@pytest.mark.asyncio
async def test_register_driver_duplicate_username(monkeypatch):
    driver_in = DriverRegister(email='driver@example.com', name='John Driver', username='taken', password='secret123')

    async def fake_get_by_username(_username: str):
        return {'id': 1, 'username': 'taken'}
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='Username already exists'):
        await UserService.create_user(driver_in)

@pytest.mark.asyncio
async def test_driver_register_schema_enforces_role():
    driver_data = {'email': 'driver@example.com', 'name': 'John Driver', 'username': 'driver1', 'password': 'secret123'}
    driver_in = DriverRegister(**driver_data)
    assert driver_in.role == UserRole.DRIVER
