import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_generate_2fa_code_success(client, monkeypatch):
    username = "testuser"

    def fake_get_current_user():
        return username

    async def fake_generate_2fa_code(_username: str):
        return "123456"

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.generate_2fa_code",
        fake_generate_2fa_code,
    )

    response = client.post("/users/2fa/generate")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "2FA code generated" in data["message"]
    assert "123456" in data["message"]


@pytest.mark.asyncio
async def test_generate_2fa_code_not_logged_in(client, monkeypatch):
    def fake_get_current_user():
        return None

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )

    response = client.post("/users/2fa/generate")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No user currently logged in" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_2fa_code_user_not_found(client, monkeypatch):
    username = "nonexistent"

    def fake_get_current_user():
        return username

    async def fake_generate_2fa_code(_username: str):
        raise ValueError("User not found")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.generate_2fa_code",
        fake_generate_2fa_code,
    )

    response = client.post("/users/2fa/generate")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_2fa_code_already_exists(client, monkeypatch):
    username = "testuser"

    def fake_get_current_user():
        return username

    async def fake_generate_2fa_code(_username: str):
        raise ValueError("2FA code already exists")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.generate_2fa_code",
        fake_generate_2fa_code,
    )

    response = client.post("/users/2fa/generate")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "2FA code already exists" in response.json()["detail"]
