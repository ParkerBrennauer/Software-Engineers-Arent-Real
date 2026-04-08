import pytest
from src.schemas import UserRole
from src.repositories import UserRepo
from src.services import RestaurantOwnerService

@pytest.mark.asyncio
async def test_assign_user_as_staff_success(monkeypatch):
    owner_user = {'id': 1, 'username': 'owner1', 'role': UserRole.RESTAURANT_OWNER, 'email': 'owner@example.com', 'name': 'Owner', 'hashed_password': 'h', 'is_active': True, 'requires_2fa': True, 'restaurant_id': 1}
    target_user = {'id': 2, 'username': 'customer1', 'role': UserRole.CUSTOMER, 'email': 'customer@example.com', 'name': 'Customer', 'hashed_password': 'h', 'is_active': True, 'requires_2fa': False}
    captured = {}

    async def fake_get_by_username(username: str):
        if username == 'owner1':
            return owner_user
        if username == 'customer1':
            return target_user
        return None

    async def fake_update_by_username(username: str, updates: dict):
        captured['username'] = username
        captured['updates'] = updates
        return {**target_user, **updates}
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    monkeypatch.setattr(UserRepo, 'update_by_username', fake_update_by_username)
    updated = await RestaurantOwnerService.assign_user_as_staff('owner1', 'customer1')
    assert captured['username'] == 'customer1'
    assert captured['updates']['role'] == UserRole.RESTAURANT_STAFF
    assert captured['updates']['requires_2fa'] is True
    assert updated.role == UserRole.RESTAURANT_STAFF

@pytest.mark.asyncio
async def test_assign_user_as_staff_owner_not_found(monkeypatch):

    async def fake_get_by_username(_username: str):
        return None
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='Owner not found'):
        await RestaurantOwnerService.assign_user_as_staff('missing_owner', 'target')

@pytest.mark.asyncio
async def test_assign_user_as_staff_not_owner_role(monkeypatch):
    user = {'id': 1, 'username': 'notowner', 'role': UserRole.CUSTOMER, 'email': 'u@example.com', 'name': 'User', 'hashed_password': 'h', 'is_active': True, 'requires_2fa': False}

    async def fake_get_by_username(_username: str):
        return user
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='User is not a restaurant owner'):
        await RestaurantOwnerService.assign_user_as_staff('notowner', 'target')

@pytest.mark.asyncio
async def test_assign_user_as_staff_target_user_not_found(monkeypatch):
    owner_user = {'id': 1, 'username': 'owner1', 'role': UserRole.RESTAURANT_OWNER, 'email': 'owner@example.com', 'name': 'Owner', 'hashed_password': 'h', 'is_active': True, 'requires_2fa': True, 'restaurant_id': 1}

    async def fake_get_by_username(username: str):
        if username == 'owner1':
            return owner_user
        return None
    monkeypatch.setattr(UserRepo, 'get_by_username', fake_get_by_username)
    with pytest.raises(ValueError, match='User not found'):
        await RestaurantOwnerService.assign_user_as_staff('owner1', 'missing')
