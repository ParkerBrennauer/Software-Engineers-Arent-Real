from fastapi import APIRouter, status
from src.schemas.user_schema import (
    UserRegister,
    UserResponse,
    UserUpdate,
    UserTwoFactorVerify,
    UserTwoFactorResponse,
    UserPasswordReset,
    UserLogin,
    AddressAdd,
)
from src.schemas.customer_schema import CustomerRegister
from src.schemas.driver_schema import DriverRegister
from src.services.user_service import UserService
from src.api.dependencies import convert_service_error
from src.services.customer_service import CustomerService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_in: UserRegister):
    new_user = await UserService.create_user(user_in)
    return new_user


@router.post(
    "/register/customer",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_customer(customer_in: CustomerRegister):
    try:
        new_customer = await UserService.create_user(customer_in)
        return new_customer
    except ValueError as err:
        raise convert_service_error(err)


@router.post(
    "/register/driver", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_driver(driver_in: DriverRegister):
    try:
        new_driver = await UserService.create_user(driver_in)
        return new_driver
    except ValueError as err:
        raise convert_service_error(err)


@router.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login_user(body: UserLogin):
    try:
        user = await UserService.login_user(body.username, body.password)
        return user
    except ValueError as err:
        raise convert_service_error(err)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user():
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    success = await UserService.logout_user(username)
    if not success:
        raise convert_service_error(ValueError("Log out failed"))
    return {"message": f"User {username} successfully logged out"}


@router.get("/current-user", status_code=status.HTTP_200_OK)
async def get_current_user():
    username = UserService.get_current_user()
    if not username:
        return {"message": "No user currently logged in", "username": None}
    return {"message": "User is logged in", "username": username}


@router.patch(
    "/{username}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def update_user(username: str, user_in: UserUpdate):
    try:
        updated_user = await UserService.update_user(username, user_in)
        return updated_user
    except ValueError as err:
        raise convert_service_error(err)


@router.post(
    "/{username}/2fa/generate",
    response_model=UserTwoFactorResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_2fa_code(username: str):
    try:
        code = await UserService.generate_2fa_code(username)
        return UserTwoFactorResponse(message=f"2FA code generated: {code}")
    except ValueError as err:
        raise convert_service_error(err)


@router.post(
    "/{username}/2fa/verify",
    response_model=UserTwoFactorResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_2fa_code(username: str, body: UserTwoFactorVerify):
    try:
        await UserService.verify_2fa_code(username, body.code)
        return UserTwoFactorResponse(
            message="2FA verification successful", requires_2fa=False
        )
    except ValueError as err:
        raise convert_service_error(err)


@router.post("/{username}/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(username: str, body: UserPasswordReset):
    try:
        await UserService.reset_password(username, body.code, body.new_password)
        return {"message": "Password reset successful"}
    except ValueError as err:
        raise convert_service_error(err)


@router.post("/addresses", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def add_address(address_in: AddressAdd):
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        updated_user = await UserService.add_address(username, address_in.address)
        return updated_user
    except ValueError as err:
        raise convert_service_error(err)


@router.get("/addresses", response_model=list[str], status_code=status.HTTP_200_OK)
async def get_addresses():
    username = UserService.get_current_user()
    if not username:
        raise convert_service_error(ValueError("No user currently logged in"))
    try:
        addresses = await UserService.get_addresses(username)
        return addresses
    except ValueError as err:
        raise convert_service_error(err)
