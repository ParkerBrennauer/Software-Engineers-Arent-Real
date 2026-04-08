import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_register_driver_success(client, monkeypatch):
    driver_payload = {'email': 'driver@example.com', 'name': 'Test Driver', 'username': 'testdriver', 'password': 'secret123'}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_save_user(user_data: dict):
        return {'id': 2, **user_data}

    async def fake_get_password_hash(_password: str):
        return 'hashed_pw'
    monkeypatch.setattr('src.services.user_service.UserRepo.get_by_username', fake_get_by_username)
    monkeypatch.setattr('src.services.user_service.UserRepo.save_user', fake_save_user)
    monkeypatch.setattr('src.services.user_service.UserService.get_password_hash', fake_get_password_hash)
    response = client.post('/users/register/driver', json=driver_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['id'] == 2

@pytest.mark.asyncio
async def test_register_driver_missing_required_fields(client):
    incomplete_payload = {'email': 'driver@example.com', 'name': 'Test Driver'}
    response = client.post('/users/register/driver', json=incomplete_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_register_driver_invalid_email(client):
    payload = {'email': 'not-an-email', 'name': 'Test Driver', 'username': 'testdriver', 'password': 'secret123'}
    response = client.post('/users/register/driver', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_register_driver_duplicate_username(client, monkeypatch):
    driver_payload = {'email': 'driver@example.com', 'name': 'Test Driver', 'username': 'taken', 'password': 'secret123'}

    async def fake_get_by_username(_username: str):
        return {'id': 1, 'username': 'taken'}
    monkeypatch.setattr('src.services.user_service.UserRepo.get_by_username', fake_get_by_username)
    response = client.post('/users/register/driver', json=driver_payload)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()['detail'] == 'Username already exists'

@pytest.mark.asyncio
async def test_register_driver_generic_error(client, monkeypatch):
    driver_payload = {'email': 'driver@example.com', 'name': 'Test Driver', 'username': 'testdriver', 'password': 'secret123'}

    async def fake_get_by_username(_username: str):
        raise ValueError('Database error')
    monkeypatch.setattr('src.services.user_service.UserRepo.get_by_username', fake_get_by_username)
    response = client.post('/users/register/driver', json=driver_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
