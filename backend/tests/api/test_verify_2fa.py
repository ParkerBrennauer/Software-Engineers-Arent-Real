import unittest.mock
import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_verify_2fa_code_success(client, monkeypatch):
    username = "testuser"
    payload = {"code": "123456"}

    def fake_get_current_user():
        return username

    async def fake_verify_2fa_code(_username: str, _code: str):
        pass

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.verify_2fa_code",
        fake_verify_2fa_code,
    )

    response = client.post("/users/2fa/verify", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "2FA verification successful" in data["message"]
    assert data["requires_2fa"] is False


@pytest.mark.asyncio
async def test_verify_2fa_code_not_logged_in(client, monkeypatch):
    payload = {"code": "123456"}

    def fake_get_current_user():
        return None

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )

    response = client.post("/users/2fa/verify", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No user currently logged in" in response.json()["detail"]


@pytest.mark.asyncio
async def test_verify_2fa_code_invalid(client, monkeypatch):
    username = "testuser"
    payload = {"code": "000000"}

    def fake_get_current_user():
        return username

    async def fake_verify_2fa_code(_username: str, _code: str):
        raise ValueError("Invalid 2FA code")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.verify_2fa_code",
        fake_verify_2fa_code,
    )

    response = client.post("/users/2fa/verify", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid 2FA code" in response.json()["detail"]


@pytest.mark.asyncio
async def test_verify_2fa_code_expired(client, monkeypatch):
    username = "testuser"
    payload = {"code": "123456"}

    def fake_get_current_user():
        return username

    async def fake_verify_2fa_code(_username: str, _code: str):
        raise ValueError("2FA code has expired")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.verify_2fa_code",
        fake_verify_2fa_code,
    )

    response = client.post("/users/2fa/verify", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "2FA code has expired" in response.json()["detail"]


@pytest.mark.asyncio
async def test_verify_2fa_code_no_code_generated(client, monkeypatch):
    username = "testuser"
    payload = {"code": "123456"}

    def fake_get_current_user():
        return username

    async def fake_verify_2fa_code(_username: str, _code: str):
        raise ValueError("No 2FA code has been generated")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.verify_2fa_code",
        fake_verify_2fa_code,
    )

    response = client.post("/users/2fa/verify", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No 2FA code has been generated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_verify_2fa_code_user_not_found(client, monkeypatch):
    username = "nonexistent"
    payload = {"code": "123456"}

    def fake_get_current_user():
        return username

    async def fake_verify_2fa_code(_username: str, _code: str):
        raise ValueError("User not found")

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.verify_2fa_code",
        fake_verify_2fa_code,
    )

    response = client.post("/users/2fa/verify", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_verify_2fa_code_missing_code(client, monkeypatch):
    def fake_get_current_user():
        return "testuser"

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    response = client.post("/users/2fa/verify", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
