from fastapi import APIRouter, HTTPException, status
from src.schemas.user_schema import (
    UserRegister,
    UserResponse,
    UserUpdate,
    UserTwoFactorVerify,
    UserTwoFactorResponse,
    UserPasswordReset,
)
from src.services.user_service import UserService

# Define the prefix for the endpoints
router = APIRouter(prefix="/users", tags=["users"])

# Input must follow the UserRegister model


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_in: UserRegister):
    new_user = await UserService.create_user(user_in)
    return new_user


@router.patch(
    "/{username}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def update_user(username: str, user_in: UserUpdate):
    try:
        updated_user = await UserService.update_user(username, user_in)
        return updated_user
    except ValueError as err:
        message = str(err)
        if message == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        if message == "Username already exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err


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
        message = str(err)
        if message == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err


@router.post(
    "/{username}/2fa/verify",
    response_model=UserTwoFactorResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_2fa_code(username: str, body: UserTwoFactorVerify):
    try:
        await UserService.verify_2fa_code(username, body.code)
        return UserTwoFactorResponse(
            message="2FA verification successful",
            requires_2fa=False,
        )
    except ValueError as err:
        message = str(err)
        if message == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err


@router.post("/{username}/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(username: str, body: UserPasswordReset):
    try:
        await UserService.reset_password(username, body.code, body.new_password)
        return {"message": "Password reset successful"}
    except ValueError as err:
        message = str(err)
        if message == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err
