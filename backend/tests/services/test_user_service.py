import pytest
from unittest.mock import AsyncMock, patch
from src.schemas.user_schema import UserRegister, UserRole
from src.services.user_service import UserService
from src.repositories.user_repo import UserRepo


@pytest.mark.asyncio
async def test_create_user_success_customer():
    user_in = UserRegister(
        email="c@example.com",
        full_name="Cust User",
        role=UserRole.CUSTOMER,
        username="cust1",
        password="secret123",
    )

    with patch.object(UserRepo, "get_by_username", AsyncMock(return_value=None)), \
            patch.object(UserRepo, "save_user", AsyncMock(return_value={
                "id": 1,
                "email": "c@example.com",
                "full_name": "Cust User",
                "role": UserRole.CUSTOMER,
                "username": "cust1",
                "hashed_password": "hashed_pw",
                "is_active": True,
                "requires_2fa": False,
            })) as save_user_mock, \
            patch.object(UserService, "get_password_hash", AsyncMock(return_value="hashed_pw")):

        created = await UserService.create_user(user_in)

        assert created.id == 1
        assert created.username == "cust1"
        payload = save_user_mock.await_args.args[0]
        assert payload["hashed_password"] == "hashed_pw"
        assert payload["requires_2fa"] is False
        assert payload["is_active"] is True
        assert "password" not in payload


@pytest.mark.asyncio
async def test_create_user_duplicate_username_raises():
    user_in = UserRegister(
        email="dup@example.com",
        full_name="Dup User",
        role=UserRole.CUSTOMER,
        username="taken",
        password="secret123",
    )

    with patch.object(UserRepo, "get_by_username", AsyncMock(return_value={"id": 10, "username": "taken"})), \
            patch.object(UserRepo, "save_user", AsyncMock()) as save_user_mock:

        with pytest.raises(ValueError, match="Username already exists"):
            await UserService.create_user(user_in)

        save_user_mock.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_driver_requires_2fa():
    user_in = UserRegister(
        email="d@example.com",
        full_name="Driver User",
        role=UserRole.DRIVER,
        username="driver1",
        password="secret123",
    )

    with patch.object(UserRepo, "get_by_username", AsyncMock(return_value=None)), \
            patch.object(UserRepo, "save_user", AsyncMock(return_value={
                "id": 2,
                "email": "d@example.com",
                "full_name": "Driver User",
                "role": UserRole.DRIVER,
                "username": "driver1",
                "hashed_password": "hashed_pw",
                "is_active": True,
                "requires_2fa": True,
            })) as save_user_mock, \
            patch.object(UserService, "get_password_hash", AsyncMock(return_value="hashed_pw")):

        await UserService.create_user(user_in)
        payload = save_user_mock.await_args.args[0]
        assert payload["requires_2fa"] is True
