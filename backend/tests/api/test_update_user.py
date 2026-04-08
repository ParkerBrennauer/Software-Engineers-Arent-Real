import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_update_user_success(client, monkeypatch):
    username = "testuser"
    payload = {"email": "newemail@example.com", "phone": "6045551234"}

    def fake_get_current_user():
        return username

    async def fake_update_user(_username: str, _user_in):
        class DummyUser:
            id = 1
            requires_2fa = False
            is_logged_in = True
            last_login = "2024-01-01 12:00:00"
            saved_addresses = []

        return DummyUser()

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.update_user", fake_update_user
    )

    response = client.patch("/users", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["requires_2fa"] is False
    assert data["is_logged_in"] is True


@pytest.mark.asyncio
async def test_update_user_not_logged_in(client, monkeypatch):
    payload = {"email": "newemail@example.com"}

    def fake_get_current_user():
        return None

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )

    response = client.patch("/users", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No user currently logged in" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user_not_found(client, monkeypatch):
    username = "nonexistent"
    payload = {"email": "newemail@example.com"}

    def fake_get_current_user():
        return username

    async def fake_update_user(_username: str, _user_in):
        raise ValueError("User not found")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.update_user", fake_update_user
    )

    response = client.patch("/users", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user_duplicate_username(client, monkeypatch):
    username = "testuser"
    payload = {"username": "existinguser"}

    def fake_get_current_user():
        return username

    async def fake_update_user(_username: str, _user_in):
        raise ValueError("Username already exists")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.update_user", fake_update_user
    )

    response = client.patch("/users", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "Username already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user_generic_error(client, monkeypatch):
    username = "testuser"
    payload = {"email": "test@example.com"}

    def fake_get_current_user():
        return username

    async def fake_update_user(_username: str, _user_in):
        raise ValueError("Failed to update user")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.update_user", fake_update_user
    )

    response = client.patch("/users", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Failed to update user" in response.json()["detail"]
