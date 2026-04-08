from datetime import datetime, timedelta, timezone
import pytest
from src.repositories.user_repo import UserRepo
from src.services.user_service import UserService

@pytest.mark.asyncio
async def test_generate_2fa_code_success(monkeypatch):
    user_data = {'id': 1, 'username': 'driver1', 'email': 'd@example.com', 'name': 'Driver', 'role': 'driver', 'hashed_password': 'h', 'is_active': True, 'requires_2fa': True}
    captured = {}

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_update_by_username(_username: str, updates: dict):
        captured['updates'] = updates
        return {**user_data, **updates}
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserRepo, 'update_by_username', fake_update_by_username)
    code = await UserService.generate_2fa_code('driver1')
    assert len(code) == 6
    assert code.isdigit()
    assert captured['updates']['two_factor_code'] == code
    assert captured['updates']['two_factor_expires_at'] is not None

@pytest.mark.asyncio
async def test_generate_2fa_code_user_not_found(monkeypatch):

    async def fake_get_by_username(_username: str):
        return None
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='User not found'):
        await UserService.generate_2fa_code('nouser')

@pytest.mark.asyncio
async def test_verify_2fa_code_success(monkeypatch):
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    user_data = {'id': 1, 'username': 'driver1', 'two_factor_code': '123456', 'two_factor_expires_at': expires}
    captured = {}

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_update_by_username(_username: str, updates: dict):
        captured['updates'] = updates
        return {**user_data, **updates}
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserRepo, 'update_by_username', fake_update_by_username)
    result = await UserService.verify_2fa_code('driver1', '123456')
    assert result is True
    assert captured['updates']['two_factor_code'] is None
    assert captured['updates']['two_factor_expires_at'] is None

@pytest.mark.asyncio
async def test_verify_2fa_code_invalid(monkeypatch):
    expires = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    user_data = {'id': 1, 'username': 'driver1', 'two_factor_code': '123456', 'two_factor_expires_at': expires}

    async def fake_get_by_username(_username: str):
        return user_data
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='Invalid 2FA code'):
        await UserService.verify_2fa_code('driver1', '000000')

@pytest.mark.asyncio
async def test_verify_2fa_code_expired(monkeypatch):
    expires = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    user_data = {'id': 1, 'username': 'driver1', 'two_factor_code': '123456', 'two_factor_expires_at': expires}
    captured = {}

    async def fake_get_by_username(_username: str):
        return user_data

    async def fake_update_by_username(_username: str, updates: dict):
        captured['updates'] = updates
        return {**user_data, **updates}
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserRepo, 'update_by_username', fake_update_by_username)
    with pytest.raises(ValueError, match='2FA code has expired'):
        await UserService.verify_2fa_code('driver1', '123456')

@pytest.mark.asyncio
async def test_verify_2fa_code_no_code_generated(monkeypatch):
    user_data = {'id': 1, 'username': 'driver1', 'two_factor_code': None, 'two_factor_expires_at': None}

    async def fake_get_by_username(_username: str):
        return user_data
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='No 2FA code has been generated'):
        await UserService.verify_2fa_code('driver1', '123456')
