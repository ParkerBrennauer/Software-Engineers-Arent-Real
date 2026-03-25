import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_assign_staff_success(client, monkeypatch):

    payload = {"staff_username": "user123"}

    owner_user = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": 10,
        "is_active": True,
    }

    target_user = {
        "id": 2,
        "username": "user123",
        "email": "user@example.com",
        "name": "User",
        "role": "customer",
        "hashed_password": "hashed",
        "is_active": True,
    }

    async def fake_get_by_username(username: str):
        if username == "owner1":
            return owner_user
        if username == "user123":
            return target_user
        return None

    async def fake_update_by_username(username: str, updates: dict):
        if username == "user123":
            return {**target_user, **updates}
        return None

    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.get_by_username",
        fake_get_by_username,
    )
    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.update_by_username",
        fake_update_by_username,
    )

    response = client.post("/restaurant_administration/owner1/staff", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 2


@pytest.mark.asyncio
async def test_assign_staff_owner_not_found(client, monkeypatch):

    payload = {"staff_username": "user123"}

    async def fake_get_by_username(_username: str):
        return None

    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.get_by_username",
        fake_get_by_username,
    )

    response = client.post("/restaurant_administration/nonexistent/staff", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Owner not found"


@pytest.mark.asyncio
async def test_assign_staff_user_not_found(client, monkeypatch):

    payload = {"staff_username": "nonexistent"}

    owner_user = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": 10,
        "is_active": True,
    }

    async def fake_get_by_username(username: str):
        if username == "owner1":
            return owner_user
        return None

    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.get_by_username",
        fake_get_by_username,
    )

    response = client.post("/restaurant_administration/owner1/staff", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_assign_staff_not_owner(client, monkeypatch):

    payload = {"staff_username": "user123"}

    customer_user = {
        "id": 1,
        "username": "customer1",
        "email": "customer@example.com",
        "name": "Customer",
        "role": "customer",
        "is_active": True,
    }

    async def fake_get_by_username(username: str):
        if username == "customer1":
            return customer_user
        return None

    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.get_by_username",
        fake_get_by_username,
    )

    response = client.post("/restaurant_administration/customer1/staff", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User is not a restaurant owner"


@pytest.mark.asyncio
async def test_assign_staff_cannot_assign_owner(client, monkeypatch):

    payload = {"staff_username": "another_owner"}

    owner_user = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": 10,
        "is_active": True,
    }

    another_owner = {
        "id": 2,
        "username": "another_owner",
        "email": "owner2@example.com",
        "name": "Owner 2",
        "role": "owner",
        "restaurant_id": 5,
        "is_active": True,
    }

    async def fake_get_by_username(username: str):
        if username == "owner1":
            return owner_user
        if username == "another_owner":
            return another_owner
        return None

    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.get_by_username",
        fake_get_by_username,
    )

    response = client.post("/restaurant_administration/owner1/staff", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Cannot assign restaurant owner as staff"


@pytest.mark.asyncio
async def test_assign_staff_already_staff(client, monkeypatch):

    payload = {"staff_username": "staff1"}

    owner_user = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": 10,
        "is_active": True,
    }

    staff_user = {
        "id": 2,
        "username": "staff1",
        "email": "staff@example.com",
        "name": "Staff",
        "role": "staff",
        "restaurant_id": 10,
        "hashed_password": "hashed",
        "is_active": True,
    }

    async def fake_get_by_username(username: str):
        if username == "owner1":
            return owner_user
        if username == "staff1":
            return staff_user
        return None

    async def fake_update_by_username(_username: str, _updates: dict):
        raise AssertionError(
            "update_by_username should not be called for existing staff"
        )

    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.get_by_username",
        fake_get_by_username,
    )
    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.update_by_username",
        fake_update_by_username,
    )

    response = client.post("/restaurant_administration/owner1/staff", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 2


@pytest.mark.asyncio
async def test_assign_staff_owner_no_restaurant(client, monkeypatch):

    payload = {"staff_username": "user123"}

    owner_user = {
        "id": 1,
        "username": "owner1",
        "email": "owner@example.com",
        "name": "Owner",
        "role": "owner",
        "restaurant_id": None,  # No restaurant assigned
        "is_active": True,
    }

    async def fake_get_by_username(username: str):
        if username == "owner1":
            return owner_user
        return None

    monkeypatch.setattr(
        "src.services.restaurant_owner_services.UserRepo.get_by_username",
        fake_get_by_username,
    )

    response = client.post("/restaurant_administration/owner1/staff", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Owner has no associated restaurant"
