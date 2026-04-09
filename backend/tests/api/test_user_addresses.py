import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_add_address_success(client, monkeypatch):
    username = "testuser"
    payload = {"address": "123 Random Blvd", "latitude": 49.0, "longitude": -119.0}

    def fake_get_current_user():
        return username

    async def fake_add_address(_username: str, _address):

        class DummyUser:
            id = 1
            requires_2fa = False
            saved_addresses = ["123 Random Blvd"]
            location = [[-119.0, 49.0]]
            is_logged_in = False
            last_login = None

        return DummyUser()

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.add_address", fake_add_address
    )

    response = client.post("/users/addresses", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["requires_2fa"] is False
    assert "saved_addresses" in data
    assert "123 Random Blvd" in data["saved_addresses"]


@pytest.mark.asyncio
async def test_add_address_user_not_found(client, monkeypatch):
    username = "unknown"
    payload = {"address": "123 Random Blvd", "latitude": 49.0, "longitude": -119.0}

    def fake_get_current_user():
        return None

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )

    response = client.post("/users/addresses", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No user currently logged in" in response.json()["detail"]


from src.schemas.user_schema import AddressAdd


@pytest.mark.asyncio
async def test_get_addresses_success(client, monkeypatch):
    username = "testuser"
    expected_addresses = [
        AddressAdd(address="123 Random Blvd", latitude=49.0, longitude=-119.0),
        AddressAdd(address="456 Side St", latitude=49.1, longitude=-119.1),
    ]

    def fake_get_current_user():
        return username

    async def fake_get_addresses(_username: str):
        return expected_addresses

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_addresses", fake_get_addresses
    )

    response = client.get("/users/addresses")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["address"] == "123 Random Blvd"
    assert response.json()[0]["longitude"] == -119.0


@pytest.mark.asyncio
async def test_get_addresses_user_not_found(client, monkeypatch):
    username = "unknown"

    def fake_get_current_user():
        return None

    monkeypatch.setattr(
        "src.api.routers.user_router.UserService.get_current_user",
        fake_get_current_user,
    )

    response = client.get("/users/addresses")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No user currently logged in" in response.json()["detail"]
