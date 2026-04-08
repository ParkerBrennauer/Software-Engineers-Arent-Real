import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_register_customer_success(client, monkeypatch):
    customer_payload = {'email': 'customer@example.com', 'name': 'Test Customer', 'username': 'testcust', 'password': 'secret123', 'payment_type': 'credit card', 'payment_details': '4532015112830366'}

    async def fake_get_by_username(_username: str):
        return None

    async def fake_save_user(user_data: dict):
        return {'id': 1, **user_data}

    async def fake_get_password_hash(_password: str):
        return 'hashed_pw'
    monkeypatch.setattr('src.services.user_service.UserRepo.get_by_username', fake_get_by_username)
    monkeypatch.setattr('src.services.user_service.UserRepo.save_user', fake_save_user)
    monkeypatch.setattr('src.services.user_service.UserService.get_password_hash', fake_get_password_hash)
    response = client.post('/users/register/customer', json=customer_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['id'] == 1
    assert data['requires_2fa'] is False

@pytest.mark.asyncio
async def test_register_customer_missing_required_fields(client):
    incomplete_payload = {'email': 'customer@example.com', 'name': 'Test Customer'}
    response = client.post('/users/register/customer', json=incomplete_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_register_customer_invalid_email(client):
    payload = {'email': 'not-an-email', 'name': 'Test Customer', 'username': 'testcust', 'password': 'secret123'}
    response = client.post('/users/register/customer', json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio
async def test_register_customer_duplicate_username(client, monkeypatch):
    customer_payload = {'email': 'customer@example.com', 'name': 'Test Customer', 'username': 'taken', 'password': 'secret123', 'payment_type': 'credit card', 'payment_details': '4532015112830366'}

    async def fake_get_by_username(_username: str):
        return {'id': 1, 'username': 'taken'}
    monkeypatch.setattr('src.services.user_service.UserRepo.get_by_username', fake_get_by_username)
    response = client.post('/users/register/customer', json=customer_payload)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()['detail'] == 'Username already exists'

@pytest.mark.asyncio
async def test_register_customer_generic_error(client, monkeypatch):
    customer_payload = {'email': 'customer@example.com', 'name': 'Test Customer', 'username': 'testcust', 'password': 'secret123', 'payment_type': 'credit card', 'payment_details': '4532015112830366'}

    async def fake_get_by_username(_username: str):
        raise ValueError('Database error')
    monkeypatch.setattr('src.services.user_service.UserRepo.get_by_username', fake_get_by_username)
    response = client.post('/users/register/customer', json=customer_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
