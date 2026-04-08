import pytest
from fastapi import status
from src.models.user_model import UserInternal

@pytest.mark.asyncio
async def test_login_success_driver(client, monkeypatch):
    user_data = {'id': 1, 'username': 'driver1', 'email': 'driver@example.com', 'name': 'John Driver', 'role': 'driver', 'hashed_password': '$2b$12$abcdefghijklmnopqrstuvwxyz', 'is_active': True, 'requires_2fa': True}

    async def fake_login_user(_username: str, _password: str):
        return UserInternal.model_validate(user_data)
    monkeypatch.setattr('src.api.routers.user_router.UserService.login_user', fake_login_user)
    payload = {'username': 'driver1', 'password': 'password123'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == 1
    assert data['requires_2fa'] is True

@pytest.mark.asyncio
async def test_login_success_customer(client, monkeypatch):
    user_data = {'id': 2, 'username': 'customer1', 'email': 'customer@example.com', 'name': 'Jane Customer', 'role': 'customer', 'hashed_password': '$2b$12$abcdefghijklmnopqrstuvwxyz', 'is_active': True, 'requires_2fa': False}

    async def fake_login_user(_username: str, _password: str):
        return UserInternal.model_validate(user_data)
    monkeypatch.setattr('src.api.routers.user_router.UserService.login_user', fake_login_user)
    payload = {'username': 'customer1', 'password': 'password123'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == 2
    assert data['requires_2fa'] is False

@pytest.mark.asyncio
async def test_login_invalid_credentials(client, monkeypatch):

    async def fake_login_user(_username: str, _password: str):
        raise ValueError('Invalid username or password')
    monkeypatch.setattr('src.api.routers.user_router.UserService.login_user', fake_login_user)
    payload = {'username': 'driver1', 'password': 'wrongpassword'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'Invalid username or password' in response.json()['detail']

@pytest.mark.asyncio
async def test_login_user_not_found(client, monkeypatch):

    async def fake_login_user(_username: str, _password: str):
        raise ValueError('Invalid username or password')
    monkeypatch.setattr('src.api.routers.user_router.UserService.login_user', fake_login_user)
    payload = {'username': 'nonexistent', 'password': 'password123'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_login_inactive_account(client, monkeypatch):

    async def fake_login_user(_username: str, _password: str):
        raise ValueError('User account is inactive')
    monkeypatch.setattr('src.api.routers.user_router.UserService.login_user', fake_login_user)
    payload = {'username': 'driver1', 'password': 'password123'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'User account is inactive' in response.json()['detail']

@pytest.mark.asyncio
async def test_login_missing_username(client):
    payload = {'password': 'password123'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_login_missing_password(client):
    payload = {'username': 'driver1'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_login_empty_username(client, monkeypatch):

    async def fake_login_user(_username: str, _password: str):
        raise ValueError('Invalid username or password')
    monkeypatch.setattr('src.api.routers.user_router.UserService.login_user', fake_login_user)
    payload = {'username': '', 'password': 'password123'}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_login_empty_password(client, monkeypatch):

    async def fake_login_user(_username: str, _password: str):
        raise ValueError('Invalid username or password')
    monkeypatch.setattr('src.api.routers.user_router.UserService.login_user', fake_login_user)
    payload = {'username': 'driver1', 'password': ''}
    response = client.post('/users/login', json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
